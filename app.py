from flask import Flask, render_template,send_file, request
import sqlite3
import numpy as np
from matplotlib import pyplot as plt
import io
import base64
import pickle

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('scattering_galaxy_data.db')
    conn.row_factory = sqlite3.Row
    return conn

def load_pkl_file(file_path):
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    return data

@app.route('/')
@app.route('/<filter_type>')
def index(filter_type=None):
    conn = get_db_connection()
    cur = conn.cursor()
    
    table_name = 'sdss_data'
    select_query = f"SELECT Scattering_INDEX, OBJID, Image, stellar_mass_median, stellar_mass_p16, stellar_mass_p84, stellar_mass_mode, stellar_mass_mean, REDSHIFT, spectrotype, SUBCLASS FROM {table_name}"
    cur.execute(select_query)
    rows_a = cur.fetchall()
    conn.close()
    
    conn = get_db_connection()
    cur = conn.cursor()
    select_query = f"SELECT Scattering_INDEX, OBJID, Image, stellar_mass_median, stellar_mass_p16, stellar_mass_p84, stellar_mass_mode, stellar_mass_mean, REDSHIFT, spectrotype, SUBCLASS FROM {table_name} where t08_odd_feature_a21_disturbed_fraction > 0.1 and t08_odd_feature_a21_disturbed_fraction != 1e+20"
    cur.execute(select_query)
    rows_d = cur.fetchall()
    conn.close()
    
    return render_template('index.html', rows_d=rows_d, rows_a=rows_a)

@app.route('/image/<scattering_index>')
def show_image(scattering_index):
    # Logic to fetch and display the image based on scattering_index
    conn = get_db_connection()
    cur = conn.cursor()
    
    table_name = 'sdss_data'
    select_query = f"SELECT Scattering_INDEX, Image, OBJID, stellar_mass_median, stellar_mass_p16, stellar_mass_p84, stellar_mass_mode, stellar_mass_mean, REDSHIFT, spectrotype, SUBCLASS, t08_odd_feature_a21_disturbed_fraction as Disturbed_Fraction, t08_odd_feature_a21_disturbed_weighted_fraction as Disturbed_weighted_Fraction, t08_odd_feature_a22_irregular_fraction as Irregular_Fraction, t08_odd_feature_a22_irregular_weighted_fraction as Irregular_weighted_fraction, t08_odd_feature_a24_merger_fraction as Merger_fraction, t08_odd_feature_a24_merger_weighted_fraction as Merger_weighted_fraction, P_EL as Elliptical, P_CW as Clockwise_Spiral, P_ACW as Anticlockwise_Spiral, P_EDGE as Edge_on_Spiral, P_MG as Merger_percentage, P_DK as Dont_know, nvote as No_Of_Votes FROM {table_name} where Scattering_INDEX = {scattering_index}"
    cur.execute(select_query)
    #cur.execute("SELECT * FROM your_table")
    row = cur.fetchone()
    conn.close()
    
    image_array = np.frombuffer(row[1], dtype=np.float32)  # Adjust dtype if necessary
    image_array = image_array.reshape((32, 32, 3))
    
    # Generate the image using Matplotlib
    fig, ax = plt.subplots()
    ax.imshow(image_array)
    ax.axis('off')  # Hide axes

    # Save the image to a BytesIO object
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
    print("datatype of scattering_index", type(scattering_index))
    table_name = 'tng_data'
    best_l2_indices = load_pkl_file("distances/best_l2_indices.pkl")
    conn = get_db_connection()
    cur = conn.cursor()
    select_query = f"SELECT Scattering_INDEX, Image_ID, Image, redshift, ratio_last, dt_last, ratio_biggest, snap_biggest, dt_biggest, stellar_mass, stellar_half_mass_radius, stellar_mass_ratio, new_redshift, merger_classification FROM {table_name} WHERE Scattering_INDEX in {tuple(best_l2_indices[int(scattering_index)])}"
    cur.execute(select_query)
    rows=cur.fetchall()
    conn.close()

    Best_L2_images = []
    for row2 in rows:
        Best_L2_image_array = np.frombuffer(row2[2], dtype=np.float32)  # Adjust dtype if necessary
        Best_L2_image_array = Best_L2_image_array.reshape((32, 32, 3))
        
        # Generate the image using Matplotlib
        fig, ax = plt.subplots()
        ax.imshow(Best_L2_image_array)
        ax.axis('off')  # Hide axes

        # Save the image to a BytesIO object
        Best_L2_img_io = io.BytesIO()
        plt.savefig(Best_L2_img_io, format='png')
        Best_L2_img_io.seek(0)
        
        # Encode image to base64 to embed in HTML
        Best_L2_img_base64 = base64.b64encode(Best_L2_img_io.getvalue()).decode('utf-8')
        
        Best_L2_images.append({
            'image_data': Best_L2_img_base64,
            'data': row2
        })
        
    best_sc_l2_inds = load_pkl_file("distances/best_sc_l2_inds.pkl")
    conn = get_db_connection()
    cur = conn.cursor()
    select_query = f"SELECT Scattering_INDEX, Image_ID, Image, redshift, ratio_last, dt_last, ratio_biggest, snap_biggest, dt_biggest, stellar_mass, stellar_half_mass_radius, stellar_mass_ratio, new_redshift, merger_classification FROM {table_name} WHERE Scattering_INDEX in {tuple(best_sc_l2_inds[int(scattering_index)])}"
    cur.execute(select_query)
    rows=cur.fetchall()
    conn.close()
    
    Best_sc_L2_images = []
    for row2 in rows:
        Best_sc_L2_image_array = np.frombuffer(row2[2], dtype=np.float32)  # Adjust dtype if necessary
        Best_sc_L2_image_array = Best_sc_L2_image_array.reshape((32, 32, 3))
        
        # Generate the image using Matplotlib
        fig, ax = plt.subplots()
        ax.imshow(Best_sc_L2_image_array)
        ax.axis('off')
        
        # Save the image to a BytesIO object
        Best_sc_L2_img_io = io.BytesIO()
        plt.savefig(Best_sc_L2_img_io, format='png')
        Best_sc_L2_img_io.seek(0)

        # Encode image to base64 to embed in HTML
        Best_sc_L2_img_base64 = base64.b64encode(Best_sc_L2_img_io.getvalue()).decode('utf-8')
        
        Best_sc_L2_images.append({
            'image_data': Best_sc_L2_img_base64,
            'data': row2
        })
        
    best_sc_l1_inds = load_pkl_file("distances/best_sc_l1_inds.pkl")
    conn = get_db_connection()
    cur = conn.cursor()
    select_query = f"SELECT Scattering_INDEX, Image_ID, Image, redshift, ratio_last, dt_last, ratio_biggest, snap_biggest, dt_biggest, stellar_mass, stellar_half_mass_radius, stellar_mass_ratio, new_redshift, merger_classification FROM {table_name} WHERE Scattering_INDEX in {tuple(best_sc_l1_inds[int(scattering_index)])}"
    cur.execute(select_query)
    rows=cur.fetchall()
    conn.close()
    
    Best_sc_L1_images = []
    for row2 in rows:
        Best_sc_L1_image_array = np.frombuffer(row2[2], dtype=np.float32)  # Adjust dtype if necessary
        Best_sc_L1_image_array = Best_sc_L1_image_array.reshape((32, 32, 3))
        
        # Generate the image using Matplotlib
        fig, ax = plt.subplots()
        ax.imshow(Best_sc_L1_image_array)
        ax.axis('off')
        
        # Save the image to a BytesIO object
        Best_sc_L1_img_io = io.BytesIO()
        plt.savefig(Best_sc_L1_img_io, format='png')
        Best_sc_L1_img_io.seek(0)
        
        # Encode image to base64 to embed in HTML
        Best_sc_L1_img_base64 = base64.b64encode(Best_sc_L1_img_io.getvalue()).decode('utf-8')
        
        Best_sc_L1_images.append({
            'image_data': Best_sc_L1_img_base64,
            'data': row2
        })
    
    return render_template('image.html', image_data=img_base64, row=row, Best_L2_images=Best_L2_images, Best_sc_L2_images=Best_sc_L2_images, Best_sc_L1_images=Best_sc_L1_images)

if __name__ == '__main__':
    app.run(debug=False)