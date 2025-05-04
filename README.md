# Laporan Proyek Machine Learning - Monica Mamondol
Ini adalah proyek akhir sistem rekomendasi. Proyek ini membangun model berbasis _content based filtering_ dan _collaborative filtering_ yang dapat menentukan top-N rekomendasi buku.
## Project Overview
![gambar buku](https://i.ibb.co.com/JWXCX65q/Screenshot-2025-05-02-130337.png)

Dalam era digital yang ditandai oleh pertumbuhan pesat informasi dan ragam produk, termasuk buku, pengguna sering kali dihadapkan pada kesulitan dalam menemukan buku yang sesuai dengan minat dan kebutuhannya. Banyaknya pilihan buku yang tersedia di perpustakaan, toko buku daring, maupun platform digital membuat proses pencarian buku menjadi semakin kompleks dan memakan waktu [[1](https://dspace.uii.ac.id/bitstream/handle/123456789/35942/17523144%20Muhammad%20Rizqi%20Az%20Zayyad.pdf?sequence=1)]. Sistem rekomendasi hadir sebagai solusi untuk membantu pengguna dalam memilih buku yang relevan dan sesuai dengan preferensi mereka. Sistem ini merupakan perangkat lunak yang dirancang untuk memberikan saran atau rekomendasi item tertentu-dalam hal ini buku-berdasarkan data preferensi, perilaku, atau riwayat interaksi pengguna sebelumnya [[2](https://bisa.ai/portofolio/detail/MzM4OQ)]. Dengan adanya sistem rekomendasi, pengguna dapat lebih mudah menemukan buku-buku yang mungkin belum mereka ketahui namun berpotensi sesuai dengan minat mereka, sehingga meningkatkan kepuasan dan pengalaman membaca [[3](https://repository.unissula.ac.id/9839/6/BAB%20I_1.pdf)].

Mengapa Proyek ini Penting Untuk Diselesaikan?

- Membantu Pembaca : Memudahkan pengguna dalam menemukan buku yang sesuai dengan minat mereka tanpa harus mencari secara manual.
- Meningkatkan Engagement Platform : Jika diterapkan di toko buku online atau perpustakaan digital, sistem rekomendasi dapat meningkatkan interaksi pengguna.
- Memanfaatkan Data Secara Optimal : Dengan menganalisis data rating, review, dan preferensi pengguna, sistem dapat memberikan insight yang bermanfaat bagi penerbit dan penulis.
- Dapat Dikembangkan Lebih Lanjut : Sistem ini dapat diintegrasikan dengan aplikasi lain seperti e-learning, perpustakaan digital, atau e-commerce buku.

## Business Understanding
Pengembangan sistem rekomendasi buku memiliki potensi besar untuk memberikan berbagai manfaat signifikan bagi para pembaca dan platform penyedia buku, baik digital maupun fisik. Sistem ini dirancang untuk menciptakan pengalaman yang lebih personal dan efisien dalam menemukan bacaan yang sesuai [[4](https://jig.rivierapublishing.id/index.php/rv/article/view/255)].

### Problem Statements
Berdasarkan latar belakang di atas, berikut ini merupakan rincian masalah yang dapat diselesaikan pada proyek ini:

- Berdasarkan data mengenai pengguna, bagaimana membuat sistem rekomendasi yang dipersonalisasi dengan teknik content-based filtering?  
- Dengan data rating yang dimiliki, bagaimana perusahaan dapat merekomendasikan buku lain yang mungkin disukai dan belum pernah dikunjungi oleh pengguna? 

### Goals
Tujuan dari proyek ini adalah:

- Menghasilkan sejumlah rekomendasi buku yang dipersonalisasi untuk pengguna dengan teknik content-based filtering.
- Menghasilkan sejumlah rekomendasi buku yang sesuai dengan preferensi pengguna dan belum pernah dikunjungi sebelumnya dengan teknik collaborative filtering.

### Solution Approach
Untuk mencapai tujuan tersebut, sistem rekomendasi ini akan menggunakan dua pendekatan utama:

- **Content-Based Filtering** Sistem ini menganalisis fitur atau konten dari item, seperti judul, deskripsi, penulis, atau kata kunci, untuk menemukan dan merekomendasikan item lain yang memiliki kemiripan dengan preferensi pengguna [[5](https://dqlab.id/content-based-filtering-dalam-algoritma-data-science)].
- **Collaborative filtering** adalah teknik dalam sistem rekomendasi yang memprediksi item yang mungkin disukai oleh pengguna berdasarkan penilaian atau preferensi pengguna lain yang memiliki kesamaan dengan pengguna tersebut. Prinsip dasarnya adalah bahwa pengguna yang memiliki preferensi serupa di masa lalu cenderung memiliki preferensi yang sama di masa depan [[6](https://kc.umn.ac.id/id/eprint/18116/7/BAB_II.pdf)]. 

## Data Understanding
### EDA - Deskripsi Variabel

| Jenis    | Keterangan                                                |
|----------|-----------------------------------------------------------|
| Title    | Book Recommendation Dataset                                      |
| Source   |[Kaggle](https://www.kaggle.com/datasets/arashnic/book-recommendation-dataset/data)                                                  |
| Maintainer | [Möbius](https://www.kaggle.com/arashnic)                                                   |
| License  | CC0: Public Domain      |
| Visibility | Publik                                                  |
| Tags     | Online Communities, Literature, Art, Recommender Systems, Culture and Humanities |
| Usability | 10.00                                                     |


**Berikut informasi pada dataset** :
 - Datasets berupa file csv (Comma-Seperated Values).
 - Dataset berupa 3 buah file CSV yaitu:
   * Books.csv
   * Ratings.csv
   * Users.csv

File `Books.csv` :

-  Dataset memiliki 271360 sample dengan 8 fitur.
 - Dataset memiliki 8 fitur `object`.
 - Terdapat *Missing value* pada fitur  `Book-Author sebanyak 2, Publisher sebanyak 2 dan Image-URL-L sebanyak 3`.
 - Tidak ada data yang duplikat.

File `Ratings.csv` :

- Dataset memiliki 1149780 sample dengan 3 fitur.
- Dataset memiliki 2 fitur `int64` dan 1 fitur `object`.
- Tidak terdapat *Missing value*.
- Tidak ada data yang duplikat.

File `Users.csv` :

- Dataset memiliki 278858 sample dengan 3 fitur.
- Dataset memiliki 1 fitur `float64`, 1 fitur `int64` dan 1 fitur `object`.
- Terdapat *Missing value* pada fitur `Age sebanyak 110762`.
- Tidak ada data yang duplikat. 

### Variable - variable pada dataset 

Kolom datasets books memiliki informasi berikut:
* **`ISBN`:** Nomor identifikasi unik untuk setiap buku (standar internasional).
* **`Book-Title`:** Judul lengkap buku.
* **`Book-Author`:** Nama penulis buku.
* **`Year-Of-Publication`:** Tahun terbit buku.
* **`Publisher`:** Nama penerbit buku.
* **`Image-URL-S`:** URL gambar sampul buku dengan ukuran (Small).
* **`Image-URL-M`:** URL gambar sampul buku dengan ukuran (Medium).
* **`Image-URL-L`:** URL gambar sampul buku dengan ukuran (Large).

Kolom datasets ratings memiliki informasi berikut:
* **`User-ID`:** Identifikasi unik untuk setiap pengguna yang memberikan rating.
* **`ISBN`:** Nomor identifikasi buku yang dirating, terkait dengan dataset books.
* **`Book-Rating`:** Nilai rating yang diberikan pengguna untuk buku tertentu.

Kolom datasets users memiliki informasi berikut:
* **`User-ID`:** Identifier unik untuk setiap pengguna, sama dengan kolom User-ID di dataset ratings.
* **`Location`:** Lokasi pengguna dalam format "kota, negara bagian, negara".
* **`Age`:** Usia pengguna dalam tahun.

Pada model kali ini dataset yang digunakan adalah file `Books.csv`, dan `Ratings.csv`.


## Referensi 
1. https://dspace.uii.ac.id/bitstream/handle/123456789/35942/17523144%20Muhammad%20Rizqi%20Az%20Zayyad.pdf?sequence=1
2. https://bisa.ai/portofolio/detail/MzM4OQ
3. https://repository.unissula.ac.id/9839/6/BAB%20I_1.pdf
4. https://jig.rivierapublishing.id/index.php/rv/article/view/255
5. https://dqlab.id/content-based-filtering-dalam-algoritma-data-science
6. https://kc.umn.ac.id/id/eprint/18116/7/BAB_II.pdf
