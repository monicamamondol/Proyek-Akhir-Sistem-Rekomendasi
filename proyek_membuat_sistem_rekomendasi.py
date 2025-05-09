# -*- coding: utf-8 -*-
"""Proyek Membuat Sistem Rekomendasi.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1HAFmFJ2kT3-Ets8g1wYmB2vwAhT-UMPw

## Import Library
"""

from google.colab import files
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import time
from tqdm import tqdm
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.metrics import precision_score, recall_score
import warnings
warnings.filterwarnings("ignore")

!pip install -q kaggle

files.upload()

!mkdir ~/.kaggle
!cp kaggle.json ~/.kaggle
!chmod 600 ~/.kaggle/kaggle.json

"""# **Data Understanding**"""

!kaggle datasets download -d arashnic/book-recommendation-dataset

!unzip /content/book-recommendation-dataset.zip

"""Dapat kita lihat setelah kita Ekstrak file zip, terdapat banyak file, tetapi pada kasus ini kita hanya menggunakan file Books.csv, Ratings.csv, dan Users.csv."""

books = pd.read_csv('/content/Books.csv')
ratings = pd.read_csv('/content/Ratings.csv')
users = pd.read_csv('/content/Users.csv')

"""## **Exploratory Data Analysis**

### **Books Variabel**
"""

books.head()

print(books.shape)

books.info()

"""Berdasarkan output di atas, kita dapat mengetahui bahwa file books.csv memiliki 271360 entri. Terdapat 8 variabel di sini, yaitu:
- ISBN: Nomor identifikasi unik untuk setiap buku (standar internasional).
- Book-Title: Judul lengkap buku.
- Book-Author: Nama penulis buku.
- Year-Of-Publication: Tahun terbit buku.
- Publisher: Nama penerbit buku.
- Image-URL-S: URL gambar sampul buku dengan ukuran (Small).
- Image-URL-M: URL gambar sampul buku dengan ukuran (Medium).
- Image-URL-L: URL gambar sampul buku dengan ukuran (Large).

### **Ratings Variabel**
"""

ratings.head()

print(ratings.shape)

ratings.info()

"""Berdasarkan output di atas, kita dapat mengetahui bahwa file ratings.csv memiliki 1149780 entri. Terdapat 3 variabel di sini, yaitu:
- User-ID: Identifikasi unik untuk setiap pengguna yang memberikan rating.
- ISBN: Nomor identifikasi buku yang dirating, terkait dengan dataset books.
- Book-Rating: Nilai rating yang diberikan pengguna untuk buku tertentu.

### **Users Variabel**
"""

users.head()

print(users.shape)

users.info()

"""Berdasarkan output di atas, kita dapat mengetahui bahwa file users.csv memiliki 1149780 entri. Terdapat 3 variabel di sini, yaitu:
- User-ID: Identifier unik untuk setiap pengguna, sama dengan kolom User-ID di dataset ratings.
- Location: Lokasi pengguna dalam format "kota, negara bagian, negara".
- Age: Usia pengguna dalam tahun.

Kita tidak menggunakan dataset users.csv

### **Univariate Analysis**
"""

# Konversi Year-Of-Publication ke numeric (handle invalid values)
books['Year-Of-Publication'] = pd.to_numeric(books['Year-Of-Publication'], errors='coerce')

# Filter tahun yang masuk akal (misalnya antara 1900-2025)
books = books[(books['Year-Of-Publication'] >= 1900) & (books['Year-Of-Publication'] <= 2025)]

# Plot distribusi tahun publikasi
plt.figure(figsize=(12,6))
sns.histplot(books['Year-Of-Publication'], bins=50)
plt.title('Distribution of Book Publication Years')
plt.xlabel('Year of Publication')
plt.ylabel('Count')
plt.show()

# Top 10 publisher dengan buku terbanyak
top_publishers = books['Publisher'].value_counts().head(10)

plt.figure(figsize=(12,6))
sns.barplot(x=top_publishers.values, y=top_publishers.index)
plt.title('Top 10 Publishers by Number of Books')
plt.xlabel('Number of Books')
plt.ylabel('Publisher')
plt.show()

# Top 10 authors dengan buku terbanyak
top_authors = books['Book-Author'].value_counts().head(10)

plt.figure(figsize=(12,6))
sns.barplot(x=top_authors.values, y=top_authors.index)
plt.title('Top 10 Authors by Number of Books')
plt.xlabel('Number of Books')
plt.ylabel('Author')
plt.show()

# Hitung statistik deskriptif rating
print(ratings['Book-Rating'].describe())

# Persentase rating eksplisit (rating > 0) vs implisit (rating = 0)
rating_types = ratings['Book-Rating'].apply(lambda x: 'Explicit' if x > 0 else 'Implicit').value_counts(normalize=True) * 100

plt.figure(figsize=(8,6))
sns.barplot(x=rating_types.index, y=rating_types.values)
plt.title('Percentage of Explicit vs Implicit Ratings')
plt.ylabel('Percentage')
plt.show()

"""### **Multivariate Analysis**"""

sns.pairplot(ratings, diag_kind = 'kde')

"""# **Data Preparation**

### **Mengatasi Missing Value dan Duplicated**

Apakah ada missing value atau tidak.
"""

books.isnull().sum()

"""Terdapat missing value di books.csv
- 2 entri penulis
- 2 entri penerbit
- 3 entri URL gambar (Large)

2-3 missing values dari total 270k entri (sangat kecil) → tidak signifikan secara statistik.
"""

books.dropna(subset=['Book-Author', 'Publisher'], inplace=True)

ratings.isnull().sum()

"""Tidak terdapat missing value di ratings.csv"""

users.isnull().sum()

"""Terdapat missing value di users.csv
- 110.762 entri usia  (bisa mencapai 40-60% dari total data).

Kita tidak menggunakan dataset users.csv karena:
- lebih dari 40% data usia tidak tersedia, sehingga tidak representatif.
- Tidak ada variabel pendukung lain (seperti gender atau preferensi) yang bisa membantu analisis berbasis usia.
- Tidak relevan untuk rekomendasi.
"""

books.duplicated().sum()

ratings.duplicated().sum()

users.duplicated().sum()

"""Tidak terdapat data yang duplikat.

### **Content Based Filtering**

Memberi nama header baru pada kolom Book-Rating dan User-ID pada rating_dataset.
"""

ratings = ratings.rename(columns={'Book-Rating': 'rating','User-ID':'user_id'})

"""Saya hanya mengambil 10000 row dari book dataset dan 5000 row untuk rating dataset."""

books = books[:10000]
ratings =ratings[:5000]

ratings.head()

"""Memberi nama header baru pada kolom Book-Title, Book-Author, Year-Of-Publication, Publisher, Image-URL-S, Image-URL-M, Image-URL-L pada books."""

books = books.rename(columns={'Book-Title': 'book_title','Book-Author':'book_author','Year-Of-Publication':'year_of_publication', 'Publisher':'publisher', 'Image-URL-S':'Image_URL_S','Image-URL-M':'Image_URL_M','Image-URL-L':'Image_URL_L'})

books.head()

"""Men-drop seluruh row yang memiliki nilai NaN."""

books = books.dropna()
ratings = ratings.dropna()

books.shape

ratings.shape

"""Mengubah dataframe dari buku menjadi sebuah list."""

book_ISBN = books['ISBN'].tolist()

book_title = books['book_title'].tolist()

book_author = books['book_author'].tolist()

book_year_of_publication = books['year_of_publication'].tolist()

"""Setelah membuat list, kita perlu membuat dictionary yang digunakan untuk memnentukan pasangan key-value pada book_ISBN, book_title, book_author, dan book_year_of_publication."""

book = pd.DataFrame({
    'book_ISBN': book_ISBN,
    'book_title': book_title,
    'book_author': book_author,
    'book_year_of_publication': book_year_of_publication
})
book

"""# **Modeling**

Pada content Based Filtering, kita akan menggunakan TF-IDF Vectorizer dan Cosine Similarity untuk membangun sistem rekomendasi.

### **TF-IDF Vectorizer**
"""

tf = TfidfVectorizer()
tf.fit(book['book_title'])
print(tf.get_feature_names_out())

"""Lakukan fit dan transformasi ke dalam matriks, pada code di bawah ini, matriks tersebut adalah tfidf_matrix."""

tfidf_matrix = tf.fit_transform(book['book_title'])

tfidf_matrix.shape

"""Pada tfidf_matrix terdapat 10000 ukuran data dan 5586 nama penulis buku.

Mengubah tfidf_matrix yang awalnya vektor menjadi matriks.
"""

tfidf_matrix.todense()

pd.DataFrame(
    tfidf_matrix.todense(),
    columns=tf.get_feature_names_out(),
    index=book.book_title
).sample(10, axis=1,replace=True).sample(10, axis=0)

"""### **Cosine Similarity**

Dalam sistem rekomendasi, kita perlu mencari cara supaya item yang kita rekomendasikan tidak terlalu jauh dari data pusat, oleh karena itu kita butuh derajat kesamaan pada item, dalam proyek ini, buku dengan derajat kesamaan antar buku dengan cosine similarity.
"""

cosine_sim = cosine_similarity(tfidf_matrix)
cosine_sim

cosine_sim_df = pd.DataFrame(cosine_sim, index=book['book_title'], columns=book['book_author'])
cosine_sim_df

"""Di bawah ini adalah fungsi untuk mendapatkan rekomendasi berbasis penulis buku dengan k sebagai jumlah rekomendasi yang diingkan, dalam fungsi ini, kita akan mendapatkan 10 rekomendasi."""

def get_recommendations(title, cosine_sim=cosine_sim):
    idx = books.index[books['book_title'] == title].tolist()[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    book_indices = [i[0] for i in sim_scores]
    return books['book_title'].iloc[book_indices]

get_recommendations('Cradle and All')

"""# **Evaluation**"""

# Definisi fungsi evaluasi
def precision_recall_at_k(recommended_items, relevant_items, k=10):
    recommended_k = recommended_items[:k]
    relevant_set = set(relevant_items)

    true_positives = len([item for item in recommended_k if item in relevant_set])
    precision = true_positives / k
    recall = true_positives / len(relevant_set) if relevant_set else 0

    return precision, recall

# Misal user menyukai buku-buku ini:
relevant = ['The Gift', 'Motherhood Is Murder', 'Gift from the Sea']

# Dan sistem merekomendasikan:
recommended = ['The Gift', 'MOTHER : MOTHER', 'Myths of Motherhood',
               'Motherhood Is Murder', 'Gift From The Sea']

precision, recall = precision_recall_at_k(recommended, relevant, k=5)
print(f'Precision@5: {precision:.2f}')
print(f'Recall@5: {recall:.2f}')

"""Hasil evaluasi tersebut menunjukkan:

- Precision@5 = 0.40
Artinya: dari 5 buku yang direkomendasikan oleh sistem, 40% (2 buku) memang relevan atau disukai oleh pengguna.
→ Sistem merekomendasikan 5 buku, dan 2 di antaranya cocok.

- Recall@5 = 0.67
Artinya: dari seluruh buku yang disukai pengguna (3 buku), 67% (2 buku) berhasil ditemukan oleh sistem dalam 5 rekomendasi teratas.
→ Sistem berhasil menemukan 2 dari 3 buku relevan.

### **Collaborative Filtering**

Pada cell code di bawah ini, kita akan meyandikan user_id menjadi integer.
"""

user_ids = ratings['user_id'].unique().tolist()

user_to_user_encoded = {x: i for i, x in enumerate(user_ids)}

user_encoded_to_user = {i: x for i, x in enumerate(user_ids)}

"""Pada cell code di bawah ini, saya akan meyandikan book_id menjadi integer."""

book_ids = ratings['ISBN'].unique().tolist()
book_to_book_encoded = {x: i for i, x in enumerate(book_ids)}
book_encoded_to_book = {i: x for i, x in enumerate(book_ids)}

ratings['user'] = ratings['user_id'].map(user_to_user_encoded)
ratings['book'] = ratings['ISBN'].map(book_to_book_encoded)

""" Kita akan cek jumlah pengguna dan jumlah buku, serta mengubah tipe data rating menjadi float."""

num_users = len(user_encoded_to_user)
print(num_users)
num_book = len(book_encoded_to_book)
print(num_book)
ratings['rating'] = ratings['rating'].values.astype(np.float32)

min_rating = min(ratings['rating'])
max_rating = max(ratings['rating'])

print('Number of User: {}, Number of Book: {}, Min Rating: {}, Max Rating: {}'.format(
    num_users, num_book, min_rating, max_rating
))

"""### **Membagi Dataset**

Sebelum kita membagi dataset menjadi data latih dan data validasi, kita terlebih dahulu harus mengacak dataset.
"""

rating_dataset = ratings.sample(frac=1, random_state=42)
rating_dataset

"""Saya membagi dataset yang ada menjadi 70% untuk latihan dan 30% untuk validasi."""

x = rating_dataset[['user', 'book']].values

y = rating_dataset['rating'].apply(lambda x: (x - min_rating) / (max_rating - min_rating)).values

train_indices = int(0.70 * rating_dataset.shape[0])
x_train, x_val, y_train, y_val = (
    x[:train_indices],
    x[train_indices:],
    y[:train_indices],
    y[train_indices:]
)

print(x, y)

"""# **Modeling**

Model yang akan kita pakai dalam sistem rekomendasi berbasis pendapat pengguna adalah RecommenderNet.
"""

from tensorflow import keras
from tensorflow.keras import layers
import tensorflow as tf

class RecommenderNet(tf.keras.Model):

  def __init__(self, num_users, num_book, embedding_size, **kwargs):
    super(RecommenderNet, self).__init__(**kwargs)
    self.num_users = num_users
    self.num_book = num_book
    self.embedding_size = embedding_size
    self.user_embedding = layers.Embedding(
        num_users,
        embedding_size,
        embeddings_initializer = 'he_normal',
        embeddings_regularizer = keras.regularizers.l2(1e-6)
    )
    self.user_bias = layers.Embedding(num_users, 1)
    self.book_embedding = layers.Embedding(
        num_book,
        embedding_size,
        embeddings_initializer = 'he_normal',
        embeddings_regularizer = keras.regularizers.l2(1e-6)
    )
    self.book_bias = layers.Embedding(num_book, 1)

  def call(self, inputs):
    user_vector = self.user_embedding(inputs[:,0])
    user_bias = self.user_bias(inputs[:, 0])
    book_vector = self.book_embedding(inputs[:, 1])
    book_bias = self.book_bias(inputs[:, 1])

    dot_user_book = tf.tensordot(user_vector, book_vector, 2)

    x = dot_user_book + user_bias + book_bias

    return tf.nn.sigmoid(x)

"""Selanjutnya kita melakukan proses compile pada model dengan binary crossentropy sebagai loss function, adam sebagai optimizer, dan RMSE sebagai metrik dari model."""

model = RecommenderNet(num_users, num_book, 50)

model.compile(
    loss = tf.keras.losses.BinaryCrossentropy(),
    optimizer = keras.optimizers.Adam(learning_rate=0.001),
    metrics=[tf.keras.metrics.RootMeanSquaredError()]
)

history = model.fit(
    x = x_train,
    y = y_train,
    batch_size = 5,
    epochs = 20,
    validation_data = (x_val, y_val)
)

"""# **Evaluation**

## **Visualisasi Metrik**

Berikut adalah hasil latihan dari data yang ada, evaluasi metrik yang digunakan adalah RMSE.
"""

plt.plot(history.history['root_mean_squared_error'])
plt.plot(history.history['val_root_mean_squared_error'])
plt.title('model_metrics')
plt.ylabel('root_mean_squared_error')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

"""Sebelumnya, kita perlu mendefinisikan ulang book_dataset dan rating_dataset."""

book_dataset =  book
rating_dataset = rating_dataset

user_id = rating_dataset.user_id.sample(1).iloc[0]
books_have_been_read_by_user = rating_dataset[rating_dataset.user_id == user_id]

books_have_not_been_read_by_user = book_dataset[book_dataset['book_ISBN'].isin(books_have_been_read_by_user.ISBN.values)]['book_ISBN']
books_have_not_been_read_by_user = list(
    set(books_have_not_been_read_by_user)
    .intersection(set(book_to_book_encoded.keys()))
)

books_have_not_been_read_by_user = [[book_to_book_encoded.get(x)] for x in books_have_not_been_read_by_user]
user_encoder = user_to_user_encoded.get(user_id)
user_book_array = np.hstack(
    ([[user_encoder]] * len(books_have_not_been_read_by_user), books_have_not_been_read_by_user)
)

ratings = model.predict(user_book_array).flatten()

top_ratings_indices = ratings.argsort()[-10:][::-1]
recommended_book_ids = [
    book_encoded_to_book.get(books_have_not_been_read_by_user[x][0]) for x in top_ratings_indices
]

top_books_recommended = (
    books_have_been_read_by_user.sort_values(
        by = 'rating',
        ascending=False
    )
    .head(5)
    .ISBN.values
)

books_row = book_dataset[book_dataset['book_ISBN'].isin(top_books_recommended)]
for row in books_row.itertuples():
    print(row.book_title, ':', row.book_author)

print('----' * 8)
print('Top 10 Book Recommendation for user: {}'.format(user_id))
print('----' * 8)

recommended_books = book_dataset[book_dataset['book_ISBN'].isin(recommended_book_ids)]
for row in recommended_books.itertuples():
    print(row.book_title, ':', row.book_author)

