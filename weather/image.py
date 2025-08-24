# import streamlit as st
# import pandas as pd
# import mysql.connector
# from mysql.connector import Error
# import json
# from datetime import datetime
# import logging
# import io

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger()
# log_stream = io.StringIO()
# stream_handler = logging.StreamHandler(log_stream)
# logger.addHandler(stream_handler)

# # Database configuration (use environment variables in production)
# DB_CONFIG = {
#     'host': '13.202.1.117',
#     'user': 'pmaroot',
#     'password': 'i1zuHSOTFBy^ZFX^B',
#     'database': 'kurators'
# }

# # Seller ID (replace with dynamic fetching in production, e.g., from session)
# SELLER_ID = 1

# def connect_to_db():
#     """Connect to the MySQL database."""
#     try:
#         connection = mysql.connector.connect(**DB_CONFIG)
#         if connection.is_connected():
#             logger.info("Connected to the kurators database")
#             return connection
#     except Error as e:
#         logger.error(f"Error connecting to MySQL: {e}")
#         return None

# def get_or_create_color(cursor, color_name):
#     """Check if color exists in the color table; if not, create it."""
#     if not color_name:
#         return 0
#     cursor.execute("SELECT id FROM color WHERE color = %s", (color_name.upper(),))
#     result = cursor.fetchone()
#     if result:
#         return result[0]
#     else:
#         cursor.execute("INSERT INTO color (color, status) VALUES (%s, %s)", (color_name.upper(), 1))
#         return cursor.lastrowid

# def insert_product(cursor, product_data):
#     """Insert a product into the products table."""
#     insert_query = """
#     INSERT INTO products (
#         category_id, sub_category_id, product_name, sku, base_url, gi_tag, gi_state,
#         short_description, description, highlights, product_tag, size, color, price,
#         offer_price, discount, stock, gift_wrap_charges, custom_product, free_shipping,
#         express_delivery, brand, product_condition, age_of_the_product, capacity,
#         item_weight, item_dimensions, theme, material, included_components,
#         special_feature, hsn_code, shipping_charges, country_of_origin,
#         expiry_date_if_applicable, manufacturer, manufactured_in_year,
#         created_by, created_at, status, thumbnail_img, digital_downloads
#     ) VALUES (
#         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
#         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
#         %s, %s, %s
#     )
#     """
#     try:
#         values = (
#             product_data.get('category_id', 0),
#             product_data.get('sub_category_id', 0),
#             product_data.get('product_name'),
#             product_data.get('sku'),
#             product_data.get('base_url'),
#             int(product_data.get('gi_tag', 0)),
#             'not_applicable' if int(product_data.get('gi_tag', 0)) == 0 else product_data.get('gi_state', 'not_applicable'),
#             product_data.get('short_description'),
#             product_data.get('description'),
#             product_data.get('highlights'),
#             product_data.get('product_tag'),
#             product_data.get('size', ''),
#             product_data.get('color', ''),
#             product_data.get('price', 0),
#             product_data.get('offer_price', 0),
#             product_data.get('discount', 0),
#             product_data.get('stock', 0),
#             product_data.get('gift_wrap_charges', 0),
#             product_data.get('custom_product', 0),
#             product_data.get('free_shipping', 0),
#             product_data.get('express_delivery', 0),
#             product_data.get('brand'),
#             product_data.get('product_condition'),
#             product_data.get('age_of_the_product'),
#             product_data.get('capacity'),
#             product_data.get('item_weight'),
#             product_data.get('item_dimensions'),
#             product_data.get('theme'),
#             product_data.get('material'),
#             product_data.get('included_components'),
#             product_data.get('special_feature'),
#             product_data.get('hsn_code'),
#             product_data.get('shipping_charges', 0),
#             product_data.get('country_of_origin'),
#             product_data.get('expiry_date_if_applicable'),
#             product_data.get('manufacturer'),
#             product_data.get('manufactured_in_year'),
#             SELLER_ID,
#             datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#             product_data.get('status', 1),
#             product_data.get('thumbnail_img'),
#             product_data.get('digital_downloads')
#         )
#         cursor.execute(insert_query, values)
#         product_id = cursor.lastrowid
#         logger.info(f"Inserted product: {product_data.get('product_name')} with ID: {product_id}")
#         return product_id
#     except Error as e:
#         logger.error(f"Error inserting product {product_data.get('product_name')}: {e}")
#         return None

# def insert_product_images(cursor, product_id, images_str, color_id=0):
#     """Insert images into the product_images table."""
#     if images_str:
#         images = [img.strip() for img in images_str.split(',') if img.strip()]
#         for img in images:
#             insert_img_query = """
#             INSERT INTO product_images (product_id, color, image_name)
#             VALUES (%s, %s, %s)
#             """
#             try:
#                 cursor.execute(insert_img_query, (product_id, color_id, img))
#                 logger.info(f"Inserted image: {img} for product ID: {product_id}, color ID: {color_id}")
#             except Error as e:
#                 logger.error(f"Error inserting image {img} for product ID {product_id}: {e}")

# def insert_variant_images(cursor, product_id, variants_data):
#     """Insert variant images, handling colors."""
#     for variant in variants_data:
#         color_name = variant.get('color', '').strip()
#         images = variant.get('images', '').strip()
#         if color_name and images:
#             color_id = get_or_create_color(cursor, color_name)
#             insert_product_images(cursor, product_id, images, color_id)

# def process_file(file):
#     """Process the uploaded Excel or CSV file."""
#     log_stream.seek(0)
#     log_stream.truncate(0)  # Clear previous logs
#     try:
#         if file.name.endswith('.xlsx'):
#             df = pd.read_excel(file)
#         elif file.name.endswith('.csv'):
#             df = pd.read_csv(file)
#         else:
#             st.error("Unsupported file format. Please upload an Excel (.xlsx) or CSV (.csv) file.")
#             return None
#         logger.info(f"Read file {file.name} with {len(df)} rows")
#         return df
#     except Exception as e:
#         logger.error(f"Error reading file {file.name}: {e}")
#         st.error(f"Error reading file: {e}")
#         return None

# def main():
#     st.title("Kurators Bulk Product Upload")
#     st.write("Upload an Excel (.xlsx) or CSV (.csv) file to add products to the kurators database.")
    
#     # File upload
#     uploaded_file = st.file_uploader("Choose an Excel or CSV file", type=['xlsx', 'csv'])
    
#     if uploaded_file is not None:
#         st.write("### File Preview")
#         df = process_file(uploaded_file)
#         if df is not None:
#             st.dataframe(df.head())  # Show first few rows
#             st.write(f"Total rows: {len(df)}")
            
#             # Upload button
#             if st.button("Start Upload"):
#                 with st.spinner("Processing..."):
#                     connection = connect_to_db()
#                     if not connection:
#                         st.error("Failed to connect to the database. Check credentials or server.")
#                         return
                    
#                     cursor = connection.cursor()
#                     success_count = 0
#                     error_count = 0
                    
#                     for index, row in df.iterrows():
#                         product_data = row.to_dict()
                        
#                         # Check if product already exists
#                         cursor.execute("SELECT id FROM products WHERE product_name = %s AND created_by = %s",
#                                      (product_data.get('product_name'), SELLER_ID))
#                         if cursor.fetchone():
#                             logger.warning(f"Product {product_data.get('product_name')} already exists for seller {SELLER_ID}, skipping")
#                             error_count += 1
#                             continue
                        
#                         # Insert product
#                         product_id = insert_product(cursor, product_data)
#                         if not product_id:
#                             error_count += 1
#                             continue
                        
#                         # Insert thumbnail image
#                         if product_data.get('thumbnail_img'):
#                             insert_product_images(cursor, product_id, product_data['thumbnail_img'])
                        
#                         # Insert additional product images
#                         if product_data.get('product_images'):
#                             insert_product_images(cursor, product_id, product_data['product_images'])
                        
#                         # Handle variants
#                         if product_data.get('variants'):
#                             try:
#                                 variants_data = json.loads(product_data['variants']) if isinstance(product_data['variants'], str) else product_data['variants']
#                                 insert_variant_images(cursor, product_id, variants_data)
#                             except json.JSONDecodeError:
#                                 logger.error(f"Invalid JSON in variants for product {product_data.get('product_name')}")
#                                 error_count += 1
#                                 continue
                        
#                         success_count += 1
                    
#                     try:
#                         connection.commit()
#                         logger.info("All changes committed successfully")
#                         st.success(f"Upload completed! {success_count} products inserted successfully, {error_count} errors.")
#                     except Error as e:
#                         logger.error(f"Error committing changes: {e}")
#                         connection.rollback()
#                         st.error(f"Error committing changes: {e}")
                    
#                     cursor.close()
#                     connection.close()
#                     logger.info("Bulk insertion completed")
                    
#                     # Display logs
#                     log_stream.seek(0)
#                     st.write("### Logs")
#                     st.text(log_stream.read())

# if __name__ == "__main__":
#     main()