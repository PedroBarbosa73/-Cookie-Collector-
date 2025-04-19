from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Website(Base):
    __tablename__ = 'websites'
    
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cookies = relationship("Cookie", back_populates="website", cascade="all, delete-orphan")

class Cookie(Base):
    __tablename__ = 'cookies'
    
    id = Column(Integer, primary_key=True)
    website_id = Column(Integer, ForeignKey('websites.id'))
    name = Column(String)
    value = Column(String)
    domain = Column(String)
    path = Column(String)
    expires = Column(DateTime, nullable=True)
    secure = Column(Boolean, default=False)
    httpOnly = Column(Boolean, default=False)
    sameSite = Column(String, nullable=True)
    
    website = relationship("Website", back_populates="cookies")

class DatabaseManager:
    def __init__(self, db_url='sqlite:///cookies.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def save_cookies(self, url, cookies_list):
        session = self.Session()
        try:
            # Get or create website
            website = session.query(Website).filter_by(url=url).first()
            if not website:
                website = Website(url=url)
                session.add(website)
                session.flush()  # Get the website ID
            
            # Delete existing cookies for this website
            session.query(Cookie).filter_by(website_id=website.id).delete()
            
            # Add new cookies
            for cookie_data in cookies_list:
                cookie = Cookie(
                    website_id=website.id,
                    name=cookie_data.get('name'),
                    value=cookie_data.get('value'),
                    domain=cookie_data.get('domain'),
                    path=cookie_data.get('path', '/'),
                    secure=cookie_data.get('secure', False),
                    httpOnly=cookie_data.get('httpOnly', False),
                    sameSite=cookie_data.get('sameSite')
                )
                
                # Handle expires timestamp
                if 'expiry' in cookie_data:
                    try:
                        cookie.expires = datetime.fromtimestamp(cookie_data['expiry'])
                    except (TypeError, ValueError):
                        cookie.expires = None
                
                session.add(cookie)
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_cookies(self, url):
        session = self.Session()
        try:
            website = session.query(Website).filter_by(url=url).first()
            if not website:
                return None
            
            cookies = []
            for cookie in website.cookies:
                cookie_dict = {
                    'name': cookie.name,
                    'value': cookie.value,
                    'domain': cookie.domain,
                    'path': cookie.path,
                    'secure': cookie.secure,
                    'httpOnly': cookie.httpOnly,
                    'sameSite': cookie.sameSite
                }
                
                # Add expiry if exists
                if cookie.expires:
                    cookie_dict['expiry'] = int(cookie.expires.timestamp())
                
                cookies.append(cookie_dict)
            
            return cookies
        finally:
            session.close()
    
    def cleanup_expired_cookies(self):
        """Remove expired cookies from the database"""
        session = self.Session()
        try:
            now = datetime.utcnow()
            session.query(Cookie).filter(
                Cookie.expires.isnot(None),
                Cookie.expires < now
            ).delete()
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def remove_website(self, url):
        """Remove a specific website and all its cookies from the database"""
        session = self.Session()
        try:
            website = session.query(Website).filter_by(url=url).first()
            if website:
                session.delete(website)  # This will also delete associated cookies due to cascade
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def remove_all_except(self, keep_url):
        """Remove all websites except the specified one"""
        session = self.Session()
        try:
            session.query(Website).filter(Website.url != keep_url).delete()
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_all_websites(self):
        """Get all websites from the database"""
        session = self.Session()
        try:
            return session.query(Website).order_by(Website.url).all()
        finally:
            session.close() 