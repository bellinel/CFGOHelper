
import logging
import os
from sqlalchemy import Column, Integer, String, Boolean, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine

Base = declarative_base()   

class Database:
    """
    Класс для работы с базой данных.
    
    Attributes:
        db_url (str): URL для подключения к базе данных
        engine: Асинхронный движок SQLAlchemy
        session_factory: Фабрика сессий для создания асинхронных сессий
        logger: Логгер для записи событий базы данных
    """
    def __init__(self, db_name: str = "bot.db"):
        """
        Инициализирует новый экземпляр базы данных.
        
        Args:
            db_name (str, optional): Имя файла базы данных. По умолчанию "bot.db".
        """
        # Создаем URL подключения для асинхронного SQLite
        self.db_url =f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        # self.db_url = f"sqlite+aiosqlite:///{db_name}"
        # Создаем асинхронный движок
        self.engine = create_async_engine(self.db_url, echo=False)
        # Создаем фабрику сессий
        self.session_factory = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        self.logger = logging.getLogger(__name__)
        
    async def init(self):
        """
        Инициализирует базу данных, создавая все необходимые таблицы.
        """
        async with self.engine.begin() as conn:
            # Создаем все таблицы, которые еще не созданы
            await conn.run_sync(Base.metadata.create_all)
            self.logger.info("База данных инициализирована")
    
    async def close(self):
        """
        Закрывает соединение с базой данных.
        """
        await self.engine.dispose()
        self.logger.info("Соединение с базой данных закрыто")




class Users(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, nullable=False, unique=True)
    name = Column(String, nullable=False)
    balance = Column(Integer, nullable=False)
    free_period = Column(Integer, nullable=False, default=3)
    is_admin = Column(Boolean, nullable=False, default=False)
    is_vip = Column(Boolean, nullable=False, default=False)








