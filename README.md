# Pantip-Libr

Pantip librarian!

---

## What is Pantip?

[Pantip](http://www.pantip.com) is the biggest online Q&A community 
in Thailand founded in 1996. Pantip stores a very large 
user-generated questions and answers in numerous topics, 
e.g., lifestyle, health, tradings, technologies, sciences, 
sports, movies, and lots of others. 

---

## What does this do?

`Pantip Librarian` downloads and analyses a bulk of 
Pantip's user-generated questions and answers with 
text mining techniques. The ultimate purpose (experimentally) 
of the project is to extract and capture potential 
patterns which make the question popular or 
negatively reacted by the users.

---

## Prerequisites

Before running the tasks, these dependencies need to me met:

- [x] [Python 3.4+](https://www.python.org/download/releases/3.4.3/)
- [x] [Apache CouchDB](http://couchdb.apache.org/)
- [x] [Ruby 2.1+](https://www.ruby-lang.org/en/news/2015/08/18/ruby-2-1-7-
released/)
- [x] [RabbitMQ](https://www.rabbitmq.com)

Make sure you have all above prerequisites installed, up and running.

---

## Prepare development environment

Suppose you have all major dependencies as listed in the previous 
section installed properly. Now you can simply run the script 
to install all development dependencies:

```bash
$ bash dev-setup.sh
```

The script basically collects and installs all Python libraries you 
need for running the library.

---

## Try it

`Pantip-Libr` is not a complex module so hopefully you can have a 
speedy first step. Following is the list of common tasks you can 
find.

---

### 1. Download Pantip threads

We have a script to fetch Pantip topics (in a specified range of IDs) 
and store them in a certain format in `CouchDB` on your local machine. 
Simply run the following command:

```
$ ./fetch
```

The script will download series of Pantip threads in the 
specified range of topic IDs and store them in the `CouchDB`.

**Caveat**: Please accept my apology. The download script doesn't 
guard against HTTP connection failures. If network glitch happens, 
the script poorly ends execution.

---

### 2. Process the downloaded threads

To process the downloaded threads, execute the following 
command. (You may notice that `fetch.py` should implicitly 
be triggered at least once before calling this.)

```
$ ./process
```

The script spawns several child processes to do the feature vectorisation, 
classification, and other processing tasks. Basically, the entire 
process will take some time to finish.

**Hint**. The subprocesses leave its access logs in the root directory 
of the repo.

**Steps of operation**

| #step | script | role |
|----|----|----|
| 1 | core/process.py | Tokenise the downloaded records and push to MQ
| 2 | core/textprocess.py | Takes the dataset out of MQ and runs machine learning


## How it got so far?

Still in experimental phase. 

**Brief Process:**

```text
text => [tfidf] => [normaliser] => [decomposition] => X1

tag  => [vectoriser] => [NMF] => [binariser] => X2

input <--- [X1:X2]

input => [feature selection] => [centroid] => clusters
```

## Dataset & Performance

The dataset of 40,000 records is collected from Pantip.com. 
33.3% of the dataset is splitted as validation. 
Following is the accuracy distribution over the various 
clustering and decomposition parameters we've conducted.

|CLUSTER    | DECOM |  N  | #FT | TAG | % TOT |  [0]  |  [1]  |  [-1]
|-----------|-------|-----|-----|-----|-------|-------|-------|--------    
|    qda    |  SVD  | 400 | None|  16 | 76.51 | 76.92 | 60.20 | 14.29 
|    qda    |  SVD  | 200 | None|  16 | 72.65 | 73.10 | 50.00 | 50.00 
|    qda    |  SVD  | 100 | None|  16 | 72.59 | 73.06 | 50.94 |  0.00 
|    qda    |  SVD  |  50 | None|  16 | 75.81 | 76.31 | 51.54 | 40.00 
|    qda    |  LDA  |  50 | None|  16 | 75.87 | 76.22 | 60.07 |  0.00 
|    qda    |  LDA  |  25 | None|  16 | 74.03 | 74.35 | 58.94 | 25.00 
|    qda    |  LDA  |  10 | None|  16 | 74.37 | 74.72 | 57.53 | 25.00 
|    qda    |  LDA  |  5  | None|  16 | 73.72 | 73.97 | 63.70 |  0.00 
|    qda    |  PCA  | 400 | None|  16 | 76.42 | 76.75 | 60.47 | 20.00 
|    qda    |  PCA  | 200 | None|  16 | 75.81 | 76.32 | 52.59 | 28.57 
|    qda    |  PCA  | 100 | None|  16 | 78.78 | 79.20 | 61.05 |  0.00 
|    qda    |  PCA  |  50 | None|  16 | 75.95 | 76.18 | 64.04 | 16.67 
|    svm    |  SVD  | 400 | None|  16 | 77.56 | 78.01 | 58.19 | 25.00 
|    svm    |  SVD  | 200 | None|  16 | 69.02 | 69.49 | 47.04 |  0.00 
|    svm    |  SVD  | 100 | None|  16 | 76.27 | 76.75 | 53.58 | 25.00 
|    svm    |  SVD  |  50 | None|  16 | 76.09 | 76.43 | 60.94 |  0.00 
|    svm    |  LDA  |  50 | None|  16 | 74.33 | 74.56 | 64.66 |  0.00 
|    svm    |  LDA  |  25 | None|  16 | 70.98 | 71.41 | 51.61 | 33.33 
|    svm    |  LDA  |  10 | None|  16 | 76.67 | 77.00 | 63.48 |  0.00 
|    svm    |  LDA  |  5  | None|  16 | 77.78 | 78.26 | 56.06 | 14.29 
|    svm    |  PCA  | 400 | None|  16 | 79.93 | 80.27 | 66.67 |  0.00 
|    svm    |  PCA  | 200 | None|  16 | 77.26 | 77.46 | 69.71 | 12.50 
|    svm    |  PCA  | 100 | None|  16 | 75.67 | 76.13 | 55.79 |  0.00 
|    svm    |  PCA  |  50 | None|  16 | 73.35 | 73.65 | 59.69 |  0.00 
|    knn    |  SVD  | 400 | None|  16 | 75.45 | 75.89 | 56.10 | 25.00 
|    knn    |  SVD  | 200 | None|  16 | 77.49 | 77.98 | 53.72 |  0.00 
|    knn    |  SVD  | 100 | None|  16 | 75.98 | 76.46 | 53.31 |  0.00 
|    knn    |  SVD  |  50 | None|  16 | 76.73 | 77.11 | 60.00 |  0.00 
|    knn    |  LDA  |  50 | None|  16 | 73.99 | 74.37 | 57.25 |  0.00 
|    knn    |  LDA  |  25 | None|  16 | 77.46 | 78.09 | 49.46 |  0.00 
|    knn    |  LDA  |  10 | None|  16 | 76.10 | 76.64 | 51.16 | 12.50 
|    knn    |  LDA  |  5  | None|  16 | 78.60 | 79.00 | 59.38 | 20.00 
|    knn    |  PCA  | 400 | None|  16 | 77.83 | 78.27 | 58.21 | 42.86 
|    knn    |  PCA  | 200 | None|  16 | 76.61 | 76.83 | 68.23 |  0.00 
|    knn    |  PCA  | 100 | None|  16 | 74.71 | 74.98 | 63.77 | 12.50 
|    knn    |  PCA  |  50 | None|  16 | 73.40 | 73.84 | 55.29 | 28.57 
|  centroid |  SVD  | 400 | None|  16 | 76.82 | 77.13 | 61.63 | 33.33 
|  centroid |  SVD  | 200 | None|  16 | 77.93 | 78.36 | 58.24 | 14.29 
|  centroid |  SVD  | 100 | None|  16 | 73.79 | 74.10 | 60.00 | 25.00 
|  centroid |  SVD  |  50 | None|  16 | 76.70 | 77.30 | 51.08 | 12.50 
|  centroid |  LDA  |  50 | None|  16 | 77.56 | 78.16 | 50.00 |  0.00 
|  centroid |  LDA  |  25 | None|  16 | 76.54 | 77.00 | 54.79 | 33.33 
|  centroid |  LDA  |  10 | None|  16 | 75.76 | 76.01 | 64.73 |  0.00 
|  centroid |  LDA  |  5  | None|  16 | 78.06 | 78.52 | 59.03 | 25.00 
|  centroid |  PCA  | 400 | None|  16 | 75.98 | 76.63 | 45.80 | 14.29 
|  centroid |  PCA  | 200 | None|  16 | 75.56 | 76.12 | 50.18 | 50.00 
|  centroid |  PCA  | 100 | None|  16 | 77.90 | 78.26 | 61.96 |  0.00 
|  centroid |  PCA  |  50 | None|  16 | 76.74 | 77.09 | 60.82 | 25.00 
|    sgd    |  SVD  | 400 | None|  16 | 76.22 | 76.62 | 58.02 |  0.00 
|    sgd    |  SVD  | 200 | None|  16 | 75.48 | 75.73 | 64.20 | 28.57 
|    sgd    |  SVD  | 100 | None|  16 | 76.12 | 76.41 | 63.79 |  0.00 
|    sgd    |  SVD  |  50 | None|  16 | 78.59 | 79.06 | 58.78 | 22.22 
|    sgd    |  LDA  |  50 | None|  16 | 74.05 | 74.65 | 45.38 | 33.33 
|    sgd    |  LDA  |  25 | None|  16 | 76.52 | 76.78 | 66.43 | 12.50 
|    sgd    |  LDA  |  10 | None|  16 | 75.90 | 76.26 | 59.55 | 37.50 
|    sgd    |  LDA  |  5  | None|  16 | 77.67 | 78.09 | 57.74 | 25.00 
|    sgd    |  PCA  | 400 | None|  16 | 73.13 | 73.59 | 51.71 | 28.57 
|    sgd    |  PCA  | 200 | None|  16 | 62.54 | 62.67 | 56.90 | 14.29 
|    sgd    |  PCA  | 100 | None|  16 | 77.74 | 78.17 | 59.56 | 12.50 
|    sgd    |  PCA  |  50 | None|  16 | 80.26 | 80.67 | 61.02 | 14.29 


> PCA has also been tested but it requires too large amount 
of memory footprint to produce a proper dense matrix as its input.

*Where*

```text
CLUSTER : Clustering algorithm
DECOM   : TFIDF to dense matrix decomposition method
N       : Dimension of feature matrix (after reduction)
FT      : Number of selection of best features
TAG     : Dimension of the target dense matrix of topic tags
%TOT    : Total accuracy
[0]     : Accuracy of the class [0] : Neutral responses
[1]     : Accuracy of the class [1] : Positive responses
[-1]    : Accuracy of the class [-1] : Negative responses
```

## Overall performance

![CHART](https://cdn.rawgit.com/starcolon/pantip-libr/master/data/radar.svg?v=5)

## Best performance of QDA clustering

![CHART](https://cdn.rawgit.com/starcolon/pantip-libr/master/data/bar-QDA.svg?v=5)

## Best performance of SVM clustering

![CHART](https://cdn.rawgit.com/starcolon/pantip-libr/master/data/bar-SVM.svg?v=5)

## Best performance of K-Nearest Neighbours clustering

![CHART](https://cdn.rawgit.com/starcolon/pantip-libr/master/data/bar-KNN.svg?v=5)

## Best performance of Nearest Centroid clustering

![CHART](https://cdn.rawgit.com/starcolon/pantip-libr/master/data/bar-CENTROID.svg?v=5)

## Best performance of SGD clustering

![CHART](https://cdn.rawgit.com/starcolon/pantip-libr/master/data/bar-SGD.svg?v=5)


---


## Significant 3rd parties

These are our brilliant prerequisites.

- [x] [Thailang4r](https://github.com/veer66/thailang4r)

---

## Licence

GPL 2.0

