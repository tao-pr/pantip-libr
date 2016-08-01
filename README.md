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

| DECOM | DIM |#FEAT|   TAG | % TOT |  [0]  |  [1]  |  [-1] |
|-------|-----|-----|-------|-------|-------|-------|-------|
|  SVD  | 400 | full|   16  | 82.48 | 82.77 | 67.35 | 100.00
|  SVD  | 200 | full|   16  | 81.30 | 81.55 | 68.37 | 100.00
|  SVD  | 100 | full|   16  | 79.60 | 79.85 | 66.33 | 100.00
|  SVD  |  50 | full|   16  | 78.44 | 78.87 | 56.12 | 100.00
|  LDA  | 400 | full|   16  | 72.30 | 73.55 | 10.20 | 66.67 
|  LDA  | 200 | full|   16  | 71.88 | 73.14 |  9.18 | 66.67 
|  LDA  | 100 | full|   16  | 72.66 | 73.93 |  9.18 | 66.67 
|  LDA  |  50 | full|   16  | 72.54 | 73.63 | 18.37 | 66.67 

> PCA has also been tested but it requires too large amount 
of memory footprint to produce a proper dense matrix as its input.

*Where*

```text
DECOM : TFIDF to dense matrix decomposition
DIM   : Dimension of the target dense matrix of topic
FEAT  : Number of selection of best features
TAG   : Dimension of the target dense matrix of topic tags
%TOT  : Total accuracy
[0]   : Accuracy of the class [0] : Neutral responses
[1]   : Accuracy of the class [1] : Positive responses
[-1]  : Accuracy of the class [-1] : Negative responses
```

---


## Significant 3rd parties

These are our brilliant prerequisites.

- [x] [Thailang4r](https://github.com/veer66/thailang4r)

---

## Licence

GPL 2.0

