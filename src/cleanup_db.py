from database import DatabaseManager

def main():
    db = DatabaseManager()
    youtube_url = "https://www.youtube.com"
    
    print("Cleaning up database...")
    print("Keeping only YouTube cookies...")
    
    # Remove all websites except YouTube
    db.remove_all_except(youtube_url)
    
    print("Database cleanup complete!")
    print("You can run 'python view_database.py' to verify the results.")

if __name__ == "__main__":
    main() 