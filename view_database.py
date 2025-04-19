from database import DatabaseManager, Website, Cookie
from sqlalchemy.orm import Session
import json
from datetime import datetime

def explain_cookie(cookie):
    # Common cookie explanations
    cookie_explanations = {
        '__utma': 'Google Analytics cookie that tracks unique visitors and their first/last visits',
        '__utmb': 'Google Analytics cookie that tracks the current session',
        '__utmc': 'Google Analytics cookie that works with __utmb to determine if a new session should be created',
        '__utmz': 'Google Analytics cookie that tracks how visitors reached the website (source, campaign, etc.)',
        '__utmt': 'Google Analytics cookie that throttles request rate',
        '_ga': 'Google Analytics cookie that distinguishes unique users',
        '_gid': 'Google Analytics cookie that distinguishes unique users for 24 hours',
        '_gat': 'Google Analytics cookie that throttles request rate'
    }
    
    # Security flag explanations
    security_explanations = {
        'secure': 'Cookie can only be sent over HTTPS connections',
        'httpOnly': 'Cookie cannot be accessed by JavaScript (protects against XSS attacks)',
        'sameSite': 'Controls when cookies are sent with cross-site requests (Lax/Strict/None)'
    }
    
    # Get cookie explanation
    explanation = cookie_explanations.get(cookie.name, 'General tracking or session cookie')
    
    # Format the cookie data
    cookie_data = {
        'name': cookie.name,
        'value': cookie.value[:20] + '...' if len(cookie.value) > 20 else cookie.value,
        'domain': cookie.domain,
        'path': cookie.path,
        'expires': cookie.expires.strftime('%Y-%m-%d %H:%M:%S') if cookie.expires else 'Session cookie (expires when browser closes)',
        'secure': 'Yes' if cookie.secure else 'No',
        'httpOnly': 'Yes' if cookie.httpOnly else 'No',
        'sameSite': cookie.sameSite or 'Not set'
    }
    
    # Add explanations
    cookie_data['explanation'] = explanation
    cookie_data['security_info'] = {
        'secure': security_explanations['secure'],
        'httpOnly': security_explanations['httpOnly'],
        'sameSite': security_explanations['sameSite']
    }
    
    return cookie_data

def main():
    db = DatabaseManager()
    session = db.Session()
    
    print("\n=== Websites in Database ===")
    websites = session.query(Website).all()
    for website in websites:
        print(f"\nWebsite: {website.url}")
        print(f"First seen: {website.created_at}")
        print(f"Last updated: {website.updated_at}")
        print("\nCookies:")
        for cookie in website.cookies:
            cookie_data = explain_cookie(cookie)
            print(f"\nCookie Name: {cookie_data['name']}")
            print(f"Purpose: {cookie_data['explanation']}")
            print(f"Value: {cookie_data['value']}")
            print(f"Domain: {cookie_data['domain']}")
            print(f"Path: {cookie_data['path']}")
            print(f"Expires: {cookie_data['expires']}")
            print("\nSecurity Settings:")
            print(f"- Secure (HTTPS only): {cookie_data['secure']} - {cookie_data['security_info']['secure']}")
            print(f"- HTTP Only: {cookie_data['httpOnly']} - {cookie_data['security_info']['httpOnly']}")
            print(f"- SameSite: {cookie_data['sameSite']} - {cookie_data['security_info']['sameSite']}")
            print("-" * 80)
    
    session.close()

if __name__ == "__main__":
    main() 