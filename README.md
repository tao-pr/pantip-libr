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

**Training with:** 10,000 Samples

|CLUSTER  | DECOM |  N  | #FT | TAG | % TOT |  [0]  |  [1]  |  [-1]
|---------|-------|-----|-----|-----|-------|-------|-------|-------
|  svm    |  SVD  | 400 | None|  16 | 98.04 | 100.00|  3.98 | 0
|  svm    |  SVD  | 200 | None|  16 | 97.98 | 100.00|  1.00 | 0
|  svm    |  SVD  | 100 | None|  16 | 97.96 | 100.00|  0    | 0
|  svm    |  SVD  |  50 | None|  16 | 97.96 | 100.00|  0    | 0
|  svm    |  LDA  |  50 | None|  16 | 98.17 | 100.00| 10.45 | 0
|  svm    |  LDA  |  25 | None|  16 | 98.90 | 100.00| 46.27 | 33.33 
|  svm    |  LDA  |  10 | None|  16 | 98.23 | 100.00| 13.43 | 0
|  svm    |  LDA  |  5  | None|  16 | 98.12 | 100.00|  7.96 | 0
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
|centroid |  SVD  | 400 | None|  16 | 81.99 | 82.28 | 67.66 | 100.00
|centroid |  SVD  | 200 | None|  16 | 79.56 | 79.81 | 67.16 | 100.00
|centroid |  SVD  | 100 | None|  16 | 79.94 | 80.23 | 65.67 | 100.00
|centroid |  SVD  |  50 | None|  16 | 77.82 | 78.31 | 53.73 | 100.00
|centroid |  LDA  |  50 | None|  16 | 72.76 | 73.91 | 16.92 | 66.67 
|centroid |  LDA  |  25 | None|  16 | 75.27 | 76.36 | 22.39 | 66.67 
|centroid |  LDA  |  10 | None|  16 | 74.73 | 75.73 | 25.87 | 66.67 
|centroid |  LDA  |  5  | None|  16 | 75.67 | 76.86 | 17.91 | 66.67 
|---------|-------|-----|-----|-----|-------|-------|-------|-------
|  qda    |  SVD  | 400 | None|  16 | 98.22 | 100.00| 12.94 | 0
|  qda    |  SVD  | 200 | None|  16 | 99.97 | 100.00| 100.00| 0
|  qda    |  SVD  | 100 | None|  16 | 72.92 | 72.39 | 100.00| 0
|  qda    |  SVD  |  50 | None|  16 | 71.93 | 71.51 | 93.53 | 0
|  qda    |  LDA  |  50 | None|  16 | 35.31 | 33.98 | 100.00| 33.33 
|  qda    |  LDA  |  25 | None|  16 | 82.57 | 83.04 | 59.20 | 100.00
|  qda    |  LDA  |  10 | None|  16 | 15.30 | 13.60 | 98.01 | 33.33 
|  qda    |  LDA  |  5  | None|  16 | 72.58 | 73.30 | 37.81 | 66.67 
|---------|-------|-----|-----|-----|-------|-------|-------|-------
|  sgd    |  SVD  | 400 | None|  16 | 24.76 | 24.08 | 57.21 | 66.67 
|  sgd    |  SVD  | 200 | None|  16 | 53.13 | 53.92 | 14.93 | 33.33 
|  sgd    |  SVD  | 100 | None|  16 | 36.97 | 36.50 | 59.20 | 66.67 
|  sgd    |  SVD  |  50 | None|  16 | 26.04 | 25.65 | 43.78 | 100.00
|  sgd    |  LDA  |  50 | None|  16 |  0.65 |  0.62 |  0.50 | 100.00
|  sgd    |  LDA  |  25 | None|  16 |  5.63 |  5.30 | 20.40 | 100.00
|  sgd    |  LDA  |  10 | None|  16 |  0.92 |  0.37 | 26.37 | 100.00
|  sgd    |  LDA  |  5  | None|  16 | 85.62 | 87.32 |  3.98 |  0.00 


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

![CHART](https://cdn.rawgit.com/starcolon/pantip-libr/master/data/radar.svg?v=2)
---


## Significant 3rd parties

These are our brilliant prerequisites.

- [x] [Thailang4r](https://github.com/veer66/thailang4r)

---

## Licence

GPL 2.0

