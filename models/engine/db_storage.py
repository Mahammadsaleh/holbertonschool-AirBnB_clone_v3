#!/usr/bin/python3
"""This module defines a class to manage file storage for hbnb clone"""


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base_model import Base
from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User
from sqlalchemy.orm import scoped_session
import os


class DBStorage:
    """This class manages storage of hbnb models"""
    __engine = None
    __session = None

    def __init__(self) -> None:
        """Creates a new FileStorage instance"""

        self.__engine = create_engine('mysql+mysqldb://{}:{}@{}/{}'
                                      .format(os.getenv('HBNB_MYSQL_USER'),
                                              os.getenv('HBNB_MYSQL_PWD'),
                                              os.getenv('HBNB_MYSQL_HOST'),
                                              os.getenv('HBNB_MYSQL_DB')),
                                      pool_pre_ping=True)
        if os.getenv('HBNB_ENV') == 'test':
            Base.metadata.drop_all(self.__engine)

    def all(self, cls=None):
        """
        Retrieves all objects from the database.

        Args:
            cls (optional): The class of objects to retrieve. If not provided,
                            all objects from all classes will be retrieved.

        Returns:
            A dictionary of objects, where the key is in the format
            "<class_name>.<object_id>" and the value is the object itself.
        """
        if cls is None:
            objs = self.__session.query(State).all()
            objs.extend(self.__session.query(City).all())
            objs.extend(self.__session.query(User).all())
            objs.extend(self.__session.query(Place).all())
            objs.extend(self.__session.query(Review).all())
            objs.extend(self.__session.query(Amenity).all())
        else:
            if type(cls) is str:
                cls = eval(cls)
            objs = self.__session.query(cls)
        return {"{}.{}".format(type(obj).__name__, obj.id): obj
                for obj in objs}

    def get(self, cls, id):
        all = self.all(cls)
        for key in list(all.keys()):
            if key == f"{cls.__name__}.{id}":
                return all[f"{key}"]
        return None

    def count(self, cls=None):
            return len(self.all(cls))

    def new(self, obj):
        """Adds new object to storage"""
        self.__session.add(obj)

    def save(self):
        """Saves storage to file"""
        self.__session.commit()

    def delete(self, obj=None):
        """Deletes obj from storage"""
        if obj:
            self.__session.delete(obj)

    def reload(self):
        """Loads storage from file"""
        Base.metadata.create_all(self.__engine)
        Session = sessionmaker(bind=self.__engine, expire_on_commit=False)
        self.__session = scoped_session(Session)()

    def close(self):
        """Call remove() method on the private session attribute"""
        self.__session.close()
        return self.__session
