bokeh_template = """
	{% from macros import embed %}
	<!DOCTYPE html>
	<html lang="en">
	  {% block head %}
	  <head>
	    {% block inner_head %}
	      <meta charset="utf-8">
	      <title>{% block title %}{{ title | e if title else "Bokeh Plot" }}{% endblock %}</title>
	      {% block preamble %}{% endblock %}
	      {% block resources %}
	        {% block css_resources %}
	          {{ bokeh_css | indent(8) if bokeh_css }}
	        {% endblock %}
	        {% block js_resources %}
	          {{ bokeh_js | indent(8) if bokeh_js }}
	        {% endblock %}
	      {% endblock %}
	      {% block postamble %}{% endblock %}
	    {% endblock %}
	  </head>
	  {% endblock %}
	  {% block body %}
	  <body>
	    {% block inner_body %}
	        <style>
	        	.pointer {
	        		style=color: transparent; 
	        		background-color: transparent; 
	        		border-color: transparent;
	        	}

	        	.bk {
	                style=font-family:helvetica;
	                font-size:12px; 
	                color:grey; 
	            }
	            .text {
	                style=font-family:helvetica; 
	                color:grey; 
	                float: left;
	            }
	            
	            .para {
	                style=font-family:helvetica;
	                font-size:12px; 
	                color:grey; 
	                margin-left: 40px; 
	                width: 400px; 
	                float: left;
	            }
	            
	            .tooltip {
	              position: relative;
	              display: inline-block;
	              
	            }
	            
	            .tooltip .tooltiptext {
	              visibility: hidden;
	              width: 100px;
	              background-color: #555;
	              color: #fff;
	              font-family:helvetica;
	              font-size: 12x;
	              text-align: center;
	              border-radius: 6px;
	              padding: 5px 0;
	              position: absolute;
	              z-index: 1;
	              bottom: 20%;
	              left: 50%;
	              margin-left: 20px;
	              opacity: 0;
	              transition: opacity 0.3s;
	            }
	            
	            .tooltip .tooltiptext::after {
	              content: "";
	              position: absolute;
	              top: 0%;
	              left: 50%;
	              margin-left: -5px;
	              border-width: 5px;
	              border-style: solid;
	              border-color: #555 transparent transparent transparent;
	            }
	            
	            .tooltip:hover .tooltiptext {
	              visibility: visible;
	              opacity: 1;
	            }
	            
	            .fa {
	              padding: 10px;
	              font-size:200px;
	              width: 10px;
	              text-align: center;
	              text-decoration: none;
	            }
	            
	            /* Add a hover effect if you want */
	            .fa:hover {
	              opacity: 0.7;
	            }
	            
	            /* Set a specific color for each brand */
	            .fa-facebook {
	              background: transparent;
	              color: #3B5998;
	            }
	            
	            .fa-linkedin {
	              background: transparent;
	              color: #007bb5;
	            }
	            
	            .fa-instagram {
	              background: transparent;
	              color: red;
	            }
	            
	            .fa-twitter {
				  background: white;
				  color: #55ACEE;
				}

	            .fa-github {
	              background: transparent;
	              color: black;
	            }
	            
	            .fa-envelope {
	              background: transparent;
	              color: red;
	            }
	            
	            .fa-file {
	              background: transparent;
	              color: #367da3;
	            }

	            a.url:link {
	              color: #e73360;
	              background-color: transparent;
	              text-decoration: none;
	            }
	    
	            a.url:visited {
	              color: #e73360;
	              background-color: transparent;
	              text-decoration: none;
	            }
	    
	            a.url:hover {
	              color: #154ba6;
	              background-color: transparent;
	              text-decoration: none;
	            }
	    
	            a.url:active {
	              color: #e73360;
	              background-color: transparent;
	              text-decoration: underline;
	            }
	            
	        </style>
	      {% block contents %}
	        {% for doc in docs %}
	          {{ embed(doc) if doc.elementid }}
	          {% for root in doc.roots %}
	            {% block root scoped %}
	              {{ embed(root) | indent(10) }}
	            {% endblock %}
	          {% endfor %}
	        {% endfor %}
	      {% endblock %}
	      {{ plot_script | indent(8) }}
	    {% endblock %}
	  </body>
	  {% endblock %}
	</html>
"""

div_space = '<div style="width: {width}px; height: 10px;"></div>'

#	<span style='text-align: center; font-size:50px;'>&nbsp;&#128170;&#127997;&#129299;</span>
div_conclusion = """
<div style="font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;">
<p> 
	Why did I go through the trouble to aggregate all this data from different devices and services?
	What's the point? For me this is a tool to help keep me motivated and accountable. Now that I have put 
	in so much effort into visualizing my data, I guess I have to keep working out to 
	produce more data to visualize... &#128170;&#127997;&#129299;
</p>
</div>
"""

div_workout_cal = """
<div style="font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;"> 
	<h2>&#128197; Workout Calendar</h2>
	<p> 
		I try to workout Mon-Fri and rest on the weekends. I have tried the 3 days on and 2 days off
		pattern as well. Although I liked that pattern better, the 5 days on 2 days off pattern usually works best
		with my schedule. Most gyms are also on this pattern. The calendar plot below shows a heatmap of 
		calories burned on a given day. Hover over or tap a date to see details of the workout.
	</p>
</div>
"""

div_header = """
<div class="header" style="style=font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 400px; float: left;">
<h1>Hasan Nagib</h1> 
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
<a href="https://www.linkedin.com/in/hnagib?_l=en_US" target="_blank" class="fa fa-linkedin" style="font-size:24px"></a>
<a href="https://github.com/hnagib" class="fa fa-github" target="_blank" style="font-size:24px"></a>
<a href="https://www.facebook.com/bigannasah/" target="_blank" class="fa fa-facebook" style="font-size:24px"></a>
<a href="https://www.instagram.com/hnagib/" target="_blank" class="fa fa-instagram" style="font-size:24px"></a>
<a href="https://twitter.com/HasanNagib/" target="_blank" class="fa fa-twitter" style="font-size:24px"></a>
<a href="mailto:hasan.nagib@gmail.com?subject = Hasan's fitness data blog&body = Hello!" class="fa fa-envelope" style="font-size:24px"></a>
<a href="https://drive.google.com/file/d/1EknQPaDBVSqB5ABQFnoCiVADLD6bsKyY/view?usp=sharing" target="_blank" class="tooltip fa fa-file" style="font-size:24px">
<span class="tooltiptext">Resume</span></a>
"""

div_intro = """
<div style="font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;">
<p>
    Welcome to my health & fitness data journal! This project was born out of my love for fitness, data & 
    <a href="https://docs.bokeh.org/en/latest/index.html" class="url" target="_blank">Bokeh</a>. The goal of this project is to aggregate and visualize 
    all of my health and fitness data from various sources. The data is sourced from my Fitbit, Polar HR10, Wahoo TickerX and 
    <a href="https://www.wodup.com" class="url" target="_blank">WodUp</a> account. Check out the GitHub <a class="url" target="_blank" href="https://github.com/hnagib/hnagib-training-dashboard">repo</a> for details of the project.
</p>
"""

div_hr_rcvry = """
<div style="style=font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;"> 
<h2>&#127939;&#127997; Workouts & Heart Rate</h2>
<p>Heart rate recovery greater than 53 bpm in 2 minutes indicates that one's biological age 
is younger than calendar age. Greater recovery HR generally correlates with better health. Check out this 
<a href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5524096/#jah32178-sec-0016title" class="url" target="_blank">meta analysis</a> 
for more on this. The bar chart below shows my 2 minute recovery heart rate following workouts. 
This is calculated automatically using data collected from my Polar HR10 or Wahoo TickerX chest straps.   
Click on any bar to see corresponding workout and HR profile.
</p>
</div>
"""

# <p>&nbsp;</p>
div_hr_zones = """
<div style="font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;">   
<p>&nbsp;</p>
<p>&nbsp;</p>
<p>I also find it useful to monitor time spend in different HR zones. This can help guide my own programming 
and help me decide when to push hard or slow down in CrossFit classes. I generally aim to keep 7 day cumulative 
peak HR zone around or under 30-45 minutes depending on the goal of a given programming cycle. 
</p>
</div>
"""


div_hr_profile = """
<div style="font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;">   
<p>
Heart rate data is sourced from <a class="url" target="_blank" href="https://www.polar.com/ca-en/products/accessories/h10_heart_rate_sensor">Polar HR10</a> 
and <a class="url" target="_blank" href="https://www.wahoofitness.com/devices/heart-rate-monitors/tickr-x/buy">Wahoo TickerX's</a> .fit files. 
The .fit files are synced to Dropbox from the Wahoo iOS app and 
parsed using the <a href="https://pypi.org/project/fitparse/" class="url" target="_blank">fitparse</a> python library.
</p>
</div>
"""


div_wod_logs="""
<div style="font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;">   
<h2>&#128217; WOD Logs</h2>
<p>I use <a href="https://www.wodup.com" class="url" target="_blank">WodUp</a> to log my workouts. Unfortunately WodUp currently does 
not have an API to retrieve this data. Workout logs are scraped from my <a href="https://www.wodup.com" class="url" target="_blank">WodUp</a> account 
using <a class="url" target="_blank" href="https://pypi.org/project/selenium/">selenium</a>. Pick a date to see the WOD and the corresponding HR profile. 
</p>
</div>
"""

div_weight_lifting = """
<div style="font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;"> 
<h2>&#127947;&#127997; Weight Lifting</h2>
<p>The views below show lift PRs for different movements and reps. 
I currently weigh ~165 lbs and my three lift total is {} lbs. 
In terms of <a href="https://strengthlevel.com/powerlifting-standards" class="url" target="_blank">powerlifting standards</a>,
I would be an intermediate lifter. My goal is to get to the advanced level (i.e. 1000 lbs) by end of 2021. 
I am hoping to get there with a 405 lbs deadlift, 355 lbs back squat & 240 lbs bench press &#129310;&#127997;
</p>
</div>
"""

# <p>&nbsp;</p>
# <p>&nbsp;</p>
div_lift_total = """
<div style="font-size:12px; font-family:helvetica; text-align: left;color:grey; margin-left: 40px; width: 400px; float: left;"> 
<h2>
<span style="color:#154ba6">Bench</span> +
<span style="color:#3f8dff">Squat</span> + 
<span style="color:#7ec4ff">Deadlift</span> = 
<span style="color:#e73360">{}</span> lbs</h2>
</div"""

div_sleep = """
<div style="font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;">
<h2>&#128564; Sleep Logs</h2>
<p>
    Sleep data is sourced from Fitbit sleep logs. 
    My goal is to average 7.5 hours of time asleep and 9 hours time in bed.
    Sleep start and end hours are plotted in 24 hour format.
</p>
</div>
"""

div_wodup = """
<div style="font-size:12px; font-family:helvetica; width: 100%; overflow: hidden;">
     <div style="margin-left: 50px; width: 350px; float: left;"> 
     {wod}
     </div>
</div>
"""

div_pr_cal_header = """
<h2>Lift PR Calendar</h2>
"""

div_program = """
<h2>Monday</h2>
    <ul>
        <li>Back Squat: 3X10 @ 225 lbs</li>
        <li>Bench Press: 3X5 @ 195 lbs</li>
        <li>Assault bike: Max cals in 15 minutes</li>
    </ul>
<h2>Tuesday</h2>
    <ul>
        <li>Ring muscle ups 10x5</li>
        <li>Handstand push ups 5x5</li>
        <li>Box pistols 5x10</li>
        <li>Assault bike: Max cals in 15 minutes</li>
    </ul>
<h2>Wednesday</h2>
    <ul>
        <li>Shoulder press: 5X8 @ 85 lbs</li>
        <li>Barbell hip thrust: 5X8 @ 225 lbs</li>
        <li>4 Rounds for time:</li>
            <ul>
                <li>4 Strict pull ups</li>
                <li>8 Burpees</li>
                <li>16 Box jumps</li>
                <li>32 Double Unders</li>
            </ul>
    </ul>
<h2>Thursday</h2>
    <ul>
        <li>Ring muscle ups 10x5</li>
        <li>Handstand push ups 5x5</li>
        <li>Box pistols 5x10</li>
        <li>Assault bike: Max cals in 15 minutes</li>
    </ul>
<h2>Friday</h2>
    <ul>
        <li>Deadlift: 5X8 @ 260 lbs</li>
        <li>Banded bench press: 5X8 @ 135 lbs</li>
        <li>4 Rounds for time:</li>
            <ul>
                <li>4 Deficit handstand push ups</li>
                <li>8 Ring dips</li>
                <li>16 Box jumps overs</li>
                <li>32 Calories of assault bike</li>
            </ul>
    </ul>
"""
