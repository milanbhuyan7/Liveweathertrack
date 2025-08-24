#!/usr/bin/env python
import psycopg2
import sys

def test_postgres_connection():
    """Test PostgreSQL connection with the provided connection string"""
    
    # Your connection string
    connection_string = "postgresql://weather_9gyr_user:GzbANKGSIsK8ygzLwJ2ZshnRmQ7sypBz@dpg-d2ld9p15pdvs73aj2e70-a.oregon-postgres.render.com/weather_9gyr"
    
    print("🔍 Testing PostgreSQL Connection...")
    print("=" * 50)
    print(f"Host: dpg-d2ld9p15pdvs73aj2e70-a.oregon-postgres.render.com")
    print(f"Database: weather_9gyr")
    print(f"User: weather_9gyr_user")
    print(f"Port: 5432")
    print("=" * 50)
    
    try:
        # Test connection
        print("🔄 Attempting to connect...")
        conn = psycopg2.connect(connection_string)
        
        print("✅ Connection successful!")
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"📊 PostgreSQL Version: {version[0]}")
        
        # Check if our tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'weather_%'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        if tables:
            print(f"\n📋 Found {len(tables)} weather tables:")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("\n❌ No weather tables found!")
        
        # Check if tables have data
        if tables:
            print(f"\n📊 Checking table data...")
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"   {table_name}: {count} records")
        
        cursor.close()
        conn.close()
        print("\n✅ Connection test completed successfully!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        return False
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_connection_alternatives():
    """Test alternative connection methods"""
    print("\n🔄 Testing alternative connection methods...")
    
    # Method 1: Direct connection parameters
    try:
        conn = psycopg2.connect(
            host="dpg-d2ld9p15pdvs73aj2e70-a.oregon-postgres.render.com",
            database="weather_9gyr",
            user="weather_9gyr_user",
            password="GzbANKGSIsK8ygzLwJ2ZshnRmQ7sypBz",
            port="5432",
            sslmode="require"  # Render requires SSL
        )
        print("✅ Direct connection successful!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Direct connection failed: {e}")
    
    # Method 2: Try without SSL
    try:
        conn = psycopg2.connect(
            host="dpg-d2ld9p15pdvs73aj2e70-a.oregon-postgres.render.com",
            database="weather_9gyr",
            user="weather_9gyr_user",
            password="GzbANKGSIsK8ygzLwJ2ZshnRmQ7sypBz",
            port="5432"
        )
        print("✅ Connection without SSL successful!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Connection without SSL failed: {e}")
    
    return False

if __name__ == "__main__":
    print("🌐 PostgreSQL Connection Test")
    print("=" * 60)
    
    # Test main connection string
    if test_postgres_connection():
        print("\n🎉 Your PostgreSQL connection is working!")
    else:
        print("\n⚠️ Main connection failed, trying alternatives...")
        test_connection_alternatives()
    
    print("\n" + "=" * 60)
    print("Test completed!")
