# Group30-Search-Extension
**[Overview](#Overview)**<br>
**[Installation and Usage](#Installation-and-Usage)**<br>

## Overview
### Group Information
Group members: Zhenning zhang, Tengjun Jin, Jiaxin Lin, Chongyu Wang.
### Project Overview
Now, there are many study materials and learning platforms. For example, in CS 510 course, we have Campuswire and Community Digital Library. However, most students don't like using these platforms when they read a paper or a blog. Because they need to log into our own platforms. Instead, they prefer using Google Search to query. And these tools return results based on general ranking algorithms, which may contain some useless information. Besides, they need to open a new webpage on their browser for google search, then copy and paste the text they want to search. It is not convenient.

In order to solve this problem, we design a Google Chrome extension of Search which based on BERT model. The extension is a compact search box located in the upper right corner of the Google Chrome browser. Users can either type queries directly into the search box or simply highlight text on a webpage using their mouse. The selected text will automatically fill the search box. The results of query are displayed in three separate sections, corresponding to the three information sources.For each section, this search extension could help filter out low-relevance learning resources to the queried text. Queries can pertain to any topic within the fields of CS 510, such as ”What is the definition of PLSA? ” or ”Recent work on Recurrent Neural Networks”.  After entering or selecting a query, users can click the ”search” button.  Then the extension will execute a ranking algorithm, PLSA or BERT, to retrieve results from three primary information sources: The Community Digital Library, Google Scholar, and Google Search. The search results are either papers or webpage such as blogs.
## Installation and Usage
### Installation
Requirement: 
- Python Version >= 3.5 and 
- Numpy installed
```Bash
python --version
```
```Bash
pip install numpy
```
We implement and run programs in the following sequence.

#### Windows 
1. Download Node.js and install from (https://nodejs.org/en/download/)
2. Clone the repository
```
git clone https://github.com/Wang-Chongyu/Group30-Search-Extension.git
```
3. Change the current directory to `server`    
```
cd Group30-Search-Extension\server
```
4. Turn on the server

```
npm install
```
```
node index.js
```
5. Upload google extension to Chome

    Visit `chrome://extensions/` in your Chrome Browser

    Click `Load unpacked` on the top left side

    Select the `dist` folder in the Group30-Search-Extension\google-extension

6. Start using the extension


#### MacOS / Linux

1. Download Node.js and install (https://nodejs.org/en/download/).  

2. Clone the repository
```
git clone https://github.com/Wang-Chongyu/Group30-Search-Extension.git
```   
3. change the current directory to `server`
```
cd Group30-Search-Extension/server
```

4. Turn on the server
```
npm install
```
```
node index.js
```

5. Install the google-extension in Google Chrome.

    Visit `chrome://extensions/` in your Chrome Browser

    Click `Load unpacked` on the top left side

    Select the `dist` folder in the Group30-Search-Extension/google-extension

6. Start to use the extension.
