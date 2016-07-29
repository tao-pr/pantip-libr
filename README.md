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

*Training with:* 14000 Samples

| DECOM | DIM |   K | % TOT |  [0]  |  [1]  |  [-1] |
|-------|-----|-----|-------|-------|-------|-------|
|  SVD  | 512 |  16 | 92.36 | 93.17 | 43.48 | 100.00|

*Where*

```text
DECOM : TFIDF to dense matrix decomposition
DIM   : Dimension of the target dense matrix
K     : Number of clusters
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

