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

**Training with:** 5000 Samples

|CLUSTER  | DECOM |  N  | #FT | TAG | % TOT |  [0]  |  [1]  |  [-1]
|---------|-------|-----|-----|-----|-------|-------|-------|-------
|  knn    |  SVD  | 400 | None|  16 | 100.00| 100.00| 100.00| 100.00
|  knn    |  SVD  | 200 | None|  16 | 100.00| 100.00| 100.00| 100.00
|  knn    |  SVD  | 100 | None|  16 | 100.00| 100.00| 100.00| 100.00
|  knn    |  SVD  |  50 | None|  16 | 100.00| 100.00| 100.00| 100.00  
|  knn    |  LDA  |  50 | None|  16 | 100.00| 100.00| 100.00| 100.00
|  knn    |  LDA  |  25 | None|  16 | 100.00| 100.00| 100.00| 100.00
|  knn    |  LDA  |  10 | None|  16 | 100.00| 100.00| 100.00| 100.00
|  knn    |  LDA  |  5  | None|  16 | 100.00| 100.00| 100.00| 100.00
|---------|-------|-----|-----|-----|-------|-------|-------|-------
|centroid |  SVD  | 400 | None|  16 | 84.14 | 84.40 | 70.41 | 100.00
|centroid |  SVD  | 200 | None|  16 | 81.60 | 81.81 | 70.41 | 100.00
|centroid |  SVD  | 100 | None|  16 | 79.46 | 79.85 | 59.18 | 100.00
|centroid |  SVD  |  50 | None|  16 | 77.00 | 77.26 | 63.27 | 100.00
|centroid |  LDA  |  50 | None|  16 | 73.56 | 74.75 | 14.29 | 66.67 
|centroid |  LDA  |  25 | None|  16 | 76.20 | 77.28 | 22.45 | 66.67 
|centroid |  LDA  |  10 | None|  16 | 75.22 | 76.36 | 18.37 | 66.67 
|centroid |  LDA  |  5  | None|  16 | 75.24 | 76.48 | 13.27 | 66.67 
|---------|-------|-----|-----|-----|-------|-------|-------|-------
|  qda    |  SVD  | 400 | None|  16 | 98.32 | 100.00| 17.35 | 0
|  qda    |  SVD  | 200 | None|  16 | 99.53 | 100.00| 78.85 | 0
|  qda    |  SVD  | 100 | None|  16 | 99.94 | 100.00| 100.00| 0
|  qda    |  SVD  |  50 | None|  16 | 74.17 | 73.70 | 100.00| 0
|  qda    |  LDA  |  50 | None|  16 | 59.76 | 58.95 | 100.00| 66.67 
|  qda    |  LDA  |  25 | None|  16 | 18.90 | 17.27 | 100.00| 33.33 
|  qda    |  LDA  |  10 | None|  16 | 28.60 | 27.52 | 82.65 | 33.33 
|  qda    |  LDA  |  5  | None|  16 | 81.70 | 82.73 | 31.63 | 33.33 
|---------|-------|-----|-----|-----|-------|-------|-------|-------
|  sgd    |  SVD  | 400 | None|  16 | 30.68 | 30.13 | 58.16 | 33.33 
|  sgd    |  SVD  | 200 | None|  16 | 55.86 | 56.95 |  2.04 | 33.33 
|  sgd    |  SVD  | 100 | None|  16 | 17.51 | 16.91 | 44.90 | 100.00
|  sgd    |  SVD  |  50 | None|  16 | 14.41 | 13.93 | 37.76 | 33.33 
|  sgd    |  LDA  |  50 | None|  16 | 16.32 | 14.88 | 88.78 |  0.00 
|  sgd    |  LDA  |  25 | None|  16 | 10.14 |  9.92 | 18.37 | 100.00
|  sgd    |  LDA  |  10 | None|  16 | 16.32 | 15.39 | 63.27 |  0.00 
|  sgd    |  LDA  |  5  | None|  16 |  1.30 |  1.22 |  2.04 | 100.00


> PCA has also been tested but it requires too large amount 
of memory footprint to produce a proper dense matrix as its input.

*Where*

```text
CLUSTER : Clustering algorithm
DECOM   : TFIDF to dense matrix decomposition
N       : Dimension of feature matrix (after reduction)
FT      : Number of selection of best features
TAG     : Dimension of the target dense matrix of topic tags
%TOT    : Total accuracy
[0]     : Accuracy of the class [0] : Neutral responses
[1]     : Accuracy of the class [1] : Positive responses
[-1]    : Accuracy of the class [-1] : Negative responses
```

![CHART](https://cdn.rawgit.com/starcolon/pantip-libr/master/data/radar.svg)
---


## Significant 3rd parties

These are our brilliant prerequisites.

- [x] [Thailang4r](https://github.com/veer66/thailang4r)

---

## Licence

GPL 2.0

