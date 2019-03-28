# Project: Make Effective Data Visualisation
***

## Introduction

The objective of this project is to create an explanatory data visualisation from a dataset that communicates a clear finding or that highlights relationships or patterns in the dataset. The dataset will be investigated and the findings will be shared in a visualisation, containing primarily explanatory but also exploratory elements.

## Dataset

The chosen dataset for this project is a dataset of football player details scraped from sofifa.com for the 2018-2019 season (as of 20th December 2018). The dataset contains with 89 columns of data for 18207 players from 651 different clubs worldwide and is freely available at [https://www.kaggle.com](https://www.kaggle.com/karangadiya/fifa19).

In order to obtain the coordinates required to plot the positions on a map, a dataset of 8259 football stadium locations was generated from [https://query.wikidata.org](https://query.wikidata.org/#SELECT%20%3Fclub%20%3FclubLabel%20%3Fvenue%20%3FvenueLabel%20%3Fcoordinates%0AWHERE%0A%7B%0A%09%3Fclub%20wdt%3AP31%20wd%3AQ476028%20.%0A%09%3Fclub%20wdt%3AP115%20%3Fvenue%20.%0A%09%3Fvenue%20wdt%3AP625%20%3Fcoordinates%20.%0A%09SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22en%22%20%7D%0A%7D).

Both datasets were reduced to remove unnecessary columns, and were combined as follows:


**Data from source 1:**

    ID ............ Unique id for every player
    Name .......... Name
    Club .......... Current club
    Value ......... Current market value
    Position ...... Position on the pitch

**Data from source 2:**

    clubLabel ..... Club name
    coordinates ... Location of home stadium (latitude, longitude)


Data processing was carried out in several steps:

- The dataset 1 was aggregated to calculate the combined squad total for each club, and then filtered to include only those clubs whose total combined squad value is over 100M Euro.
- The player positions were categorised as one of [Goalkeeper, Defense, Midfield, Forward].
- The data was then enriched by adding Latitude and Longitude, extracted from dataset 2.
- Several of the entries were edited manually due to differences in spelling between the club names in each dataset.
- Several missing locations were obtained from Google Maps.
- The resulting dataset was ordered by total club value and player value to control the plotting order in the visualisation.

**Final dataset:**

    ID ............ Unique id for each player
    Name .......... Name
    Club .......... Current club
    Latitude ...... Location of home stadium (Latitude)
    Longitude ..... Location of home stadium (Longitude)
    Value ......... Current market value
    Category ...... Player category

The final dataset contains details of 3345 players for 114 different clubs.

***

## Visualisation

### Summary

The data visualisation is intended to answer the following question:

*Where is all the money in football?*

Using the market value of each player as a metric, the combined squad value of each club has been calculated. The final dataset has been limited to include only those clubs whose total combined squad value is over 100M Euro. The totals are plotted on a map at the location of the club's home ground, and linked bar charts are included below the map to show each team or player in relation to the other teams or players.

### Design

The design includes a map to provide positional encoding of each club's location to help answer the *where* part of the question. The total combined squad value of the club is encoded using size, with the locations plotted as circles whose area is proportional to the value.

A linked bar chart is also provided which duplicates this data. This practice is usually discouraged, but in this case is required to facilitate selection of clubs whose circles are co-located or heavily overplotted. Colour encoding is used to identify the selected team in both the map and the linked bar chart.

The overall visualisation is designed to instantly deliver the answer to the question, with the majority of datapoints found to be in Europe. A viewer-driven approach is used with the viewer free to interact with all the datapoints. Hovering over a club on the map or the bar chart displays the club name and total combined squad value for that club. Selecting any club allows the viewer to drill-down to more detailed information about the players for that club. Hovering over a player on the bar chart displays the player name and value for that player.

The visualisation was created using d3.js and includes both animation and interaction. The initial version can be found here: [Version 1](.\index_1.html).

Following feedback, several changes were made to the visualisation:

#### Feedback #1:
- A function was added to zoom in on the selected team since it was difficult to see which team was selected in heavily overplotted areas.
- The player categories were added to the player information when hovering over a player on the bar chart.
- The location of Hannover 96 was corrected from Africa to Germany.

Version 2 of the visualisation can be found here: [Version 2](.\index_2.html).

#### Feedback #2:
- A background was added to the map to depict the sea, and the map colours were softened.
- The CSV file was fixed to correct the special characters in player names.
- All displayed values were rounded to 2 decimal places so that number formatting was consistent.
- A label was added to the x-axis of the bar charts to identify whether the data is for clubs or players.

Version 3 of the visualisation can be found here: [Version 3](.\index_3.html).

#### Feedback #3:
- The ability to click anywhere on the map to return to initial view was added.
- A pop-up was added to display instructions & data source.

The final version of the visualisation can be found here: [Final Version](.\index_final.html).

### Feedback

The visualisation was shared with several friends and colleagues at various stages during its development. They were asked to explore the graphic and provide constructive criticism, in particular answering the following questions:

> **1) What do you notice in the visualization?**

> **2) What questions do you have about the data?**

> **3) What relationships do you notice?**

> **4) What do you think is the main takeaway from this visualization?**

> **5) Is there something you don’t understand in the graphic?**

#### Feedback #1:

> **1)	What do you notice in the visualization?**

> *It is clear that the most expensive clubs are in Europe*

> **2)	What questions do you have about the data?**

> *It would be nice to see the positions of each player. Also, the map shows a club in Africa called Hannover 96 - shouldn't this be in Germany?*

> **3)	What relationships do you notice?**

> *Highlighting the clubs on the map also highlights the clubs in the chart below it, and vice-versa. This is useful when trying to pick out a club where the map is cluttered. When a club is selected, it may be useful to zoom in on the map since some of the circles are partly hidden by other circles. You can pick out the big clubs easily. Their circles are much bigger.*

> **4)	What do you think is the main takeaway from this visualization?**

> *Most of the money in football is in Europe. While many of the World's most expensive players may not be from Europe, they play for European clubs (Messi - Barcelona, Neymar - Paris Saint-Germain).*

> **5)	Is there something you don’t understand in the graphic?**

> *It is self-explanatory.*

#### Feedback #2:

> **1)	What do you notice in the visualization?**

> *The most expensive clubs are all based in Europe.*

> **2)	What questions do you have about the data?**

> *Would it be possible to label the X axis in the chart, to differentiate between players and team? Some of the names have spurious characters. The figures are a bit confusing can you round the figures up to less decimal places?*

> **3)	What relationships do you notice?**

> *There is a link from the bar chart to the respective club on the MAP, this also works the other way round, very impressive visualisation. Would it be possible to differentiate between land and sea?*

> **4)	What do you think is the main takeaway from this visualization?**

> *The main takeaway from this visualisation I noticed, is as stated above, the majority of the money in football are shared between European clubs.*

> **5)	Is there something you don’t understand in the graphic?**

> *No self-explanatory.*

#### Feedback #3:

> *First of all, I really like your data visualisation (really cool!), and how you solve the complicated interaction with this type of visualisation.*

> **1)	What do you notice in the visualization?**

> *All money is in Europe. Your visualisation has interactive and animated elements.*

> **2)	What questions do you have about the data?**

> *Where did you get the data from? And how current is the dataset?*

> **3)	What relationships do you notice?**

> *When I click on the bubble in the chart, I can see the player value in the bar chart. But as a suggestion, would it be possible to return to initial view by clicking anywhere in the map, rather than just bubbles. I also noticed when you click on the bubble, team value appears on the bottom of the map, and team players are ranked in order of value. I can easily hover over the bar chart, and pick up a team on the map as well.*

> **4)	What do you think is the main takeaway from this visualization?**

> *All money is in Europe! UK, Spain and Italy are the top three when it comes to most expensive teams. It is surprising for me to see a team from China on this map, but on reflection, it makes sense.*

> **5)	Is there something you don’t understand in the graphic?**

> *For me, all is clear other than suggestions above.*

### Resources

https://www.kaggle.com/karangadiya/fifa19

https://opendata.stackexchange.com/questions/10047/any-open-dataset-for-football-stadium-coordinates

[https://query.wikidata.org/#SELECT%20%3Fclub%20%3FclubLabel%20%3Fvenue%20%3FvenueLabel%20%3
Fcoordinates%0AWHERE%0A%7B%0A%09%3Fclub%20wdt%3AP31%20wd%3AQ476028%20.%0A%09%3Fclub%20wdt%3AP115%20%3
Fvenue%20.%0A%09%3Fvenue%20wdt%3AP625%20%3Fcoordinates%20.%0A%09SERVICE%20wikibase%3Alabel%20%7B%20bd%3
AserviceParam%20wikibase%3Alanguage%20%22en%22%20%7D%0A%7D](https://query.wikidata.org/#SELECT%20%3Fclub%20%3FclubLabel%20%3Fvenue%20%3FvenueLabel%20%3Fcoordinates%0AWHERE%0A%7B%0A%09%3Fclub%20wdt%3AP31%20wd%3AQ476028%20.%0A%09%3Fclub%20wdt%3AP115%20%3Fvenue%20.%0A%09%3Fvenue%20wdt%3AP625%20%3Fcoordinates%20.%0A%09SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22en%22%20%7D%0A%7D)

https://www.google.com/maps/

https://www.tutorialspoint.com/d3js/index.htm

https://bl.ocks.org/gcmsrc/0e3f3f804a4e53f498ed23d58562b0ae

https://bl.ocks.org/john-guerra/43c7656821069d00dcbc

https://www.w3schools.com/colors/colors_names.asp

