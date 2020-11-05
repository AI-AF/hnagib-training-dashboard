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
	            .text {
	                style=font-family:courier; 
	                color:grey; 
	                float: left;
	            }
	            
	            .para {
	                style=font-family:courier; 
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
	              font-family:courier;
	              font-size: 75%;
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

div_conclusion = """
<div class="para"> 
	<span style='text-align: center; font-size:50px;'>&nbsp;&#128170;&#127997;&#129299;</span>
		<p> 
		So why did I go through the trouble to aggregate all this data from different devices and services?
		What's the point? For me this is a tool to help keep me motivated and accountable. Now that I have put 
		in so much effort into visualizing my data, I guess I have to keep working out to 
		produce more data to visualize... ¯\_(ツ)_/¯
	</p>
</div>
"""

div_workout_cal = """
<div style="style=font-family:courier; color:grey; margin-left: 40px; width: 450px; float: left;"> 
	<h2>&#128197; Workout Calendar</h2>
	<p> 
		I have experimented with the 3 days on and 1 day off pattern. Unfortunately, most CrossFit gyms are 
		on a 5 days on and 2 days off pattern. I also like this for consistency and routine. This way I always get
		rest days on the weekends. The calendar plot below shows a heatmap of calories burned on a given day. Hover over 
		or tap a date to see details of the workout.
	</p>
</div>
"""

div_header = """
<div style="style=font-family:courier; color:grey; margin-left: 40px; width: 400px; float: left;">
<h1>Hasan Nagib</h1> 
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
<a href="https://www.linkedin.com/in/hnagib?_l=en_US" class="fa fa-linkedin" style="font-size:24px"></a>
<a href="https://github.com/hnagib" class="fa fa-github" style="font-size:24px"></a>
<a href="https://www.facebook.com/bigannasah/" class="fa fa-facebook" style="font-size:24px"></a>
<a href="https://www.instagram.com/hnagib/" class="fa fa-instagram" style="font-size:24px"></a>
<a href="mailto:hasan.nagib@gmail.com?subject = Hasan's fitness data blog&body = Hello!" class="fa fa-envelope" style="font-size:24px"></a>
<a href="https://s3.amazonaws.com/hnagib.com/Hasan-Nagib-Resume.pdf" class="tooltip fa fa-file" style="font-size:24px">
<span class="tooltiptext">Resume</span></a>
"""

div_intro = """
<div style="style=font-family:courier; color:grey; margin-left: 40px; width: 450px; float: left;">
<p>
    Welcome to my health & fitness data journal! This project was born out of my love for fitness, data & 
    <a href="https://docs.bokeh.org/en/latest/index.html" class="url">Bokeh</a>. This is a simple static 
    Bokeh dashboard hosted on AWS S3. The data is sourced from my Fitbit, Polar HR10, Wahoo TickerX and WodUp.com 
    account. The data is refreshed by a daily batch job that runs on my local machine. Check out my GitHub for 
    details of the project.
</p>
"""

div_sleep = """
<div style="style=font-family:courier; color:grey; margin-left: 40px; width: 450px; float: left;">
<h2>&#128564; Sleep Logs</h2>
<p>
    Sleep data is sourced from Fitbit sleep logs. 
    My goal is to average 7.5 hours of time asleep and 9 hours time in bed.
    Sleep start and end hours are plotted in 24 hour format.
</p>
</div>
"""

div_hr_rcvry = """
<div style="style=font-family:courier; color:grey; margin-left: 40px; width: 450px; float: left;"> 
<h2>&#127939;&#127997; Workouts & Heart Rate</h2>
<p>Heart rate recovery greater than 53 bpm in 2 minutes indicates that one's biological age 
is younger than calendar age. Greater recovery HR generally correlates with better health. Check out this 
<a href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5524096/#jah32178-sec-0016title" class="url">meta analysis</a> 
for more on this. The bar chart below shows my 2 minute recovery heart rate following workouts. 
This is calculated automatically using data collected from my Polar HR10 or Wahoo TickerX chest straps.   
Click on any bar to see corresponding workout and HR profile.
</p>
</div>
"""

# <p>&nbsp;</p>
div_hr_zones = """
<div style="style=font-family:courier; color:grey; margin-left: 40px; width: 450px; float: left;">   
<p>&nbsp;</p>
<p>&nbsp;</p>
<p>I also find it useful to monitor time spend in different HR zones. This can help guide my own programming 
and help me decide when to push hard or slow down in CrossFit classes. I generally aim to keep 7 day cumulative 
peak HR zone around or under 30-45 minutes depending on the goal of a given programming cycle. 
</p>
</div>
"""


div_hr_profile = """
<div style="style=font-family:courier; color:grey; margin-left: 40px; width: 450px; float: left;">   
<p>
Heart rate data is sourced from Polar HR10 and Wahoo TickerX's .fit files. 
The .fit files are synced to Dropbox from the Wahoo iOS app and 
parsed using the <a href="https://pypi.org/project/fitparse/" class="url">fitparse</a> python library.
</p>
</div>
"""


div_wod_logs="""
<div style="style=font-family:courier; color:grey; margin-left: 40px; width: 450px; float: left;">   
<h2>&#128217; WOD Logs</h2>
<p>I use <a href="https://www.wodup.com" class="url">WodUp</a> to log my workouts. Unfortunately WodUp currently does 
not have an API to retrieve this data. Workout data is sourced from my <a href="https://www.wodup.com" class="url">WodUp</a> account. 
The data is scraped using selenium. Pick a date to see the WOD and the corresponding HR profile. 
</p>
</div>
"""

div_weight_lifting = """
<div style="style=font-family:courier; color:grey; margin-left: 40px; width: 400px; height: 180px; float: left;"> 
<h2>&#127947;&#127997; Weight Lifting</h2>
<p>The views below show lift PRs for different movements and reps. 
I currently weigh ~170 lbs and my three lift total is {} lbs. 
In terms of <a href="https://strengthlevel.com/powerlifting-standards" class="url">powerlifting standards</a>,
I would be an intermediate lifter. My goal is to get to the advanced level (i.e. 1000 lbs) by end of 2021. 
I am hoping to get there with a 405 lbs deadlift, 355 lbs back squat & 240 lbs bench press &#129310;&#127997;
</p>
</div>
"""

div_lift_total = """
<div style="style=font-family:courier; text-align: center;color:grey; margin-left: 40px; width: 400px; float: left;"> 
<h2>
<p>&nbsp;</p>
<p>&nbsp;</p>
<span style="color:#154ba6">Bench</span> +
<span style="color:#3f8dff">Squat</span> + 
<span style="color:#7ec4ff">Deadlift</span> = 
<span style="color:#e73360">{}</span> lbs</h2>
</div"""

div_wodup = """
<div style="width: 100%; overflow: hidden;">
     <div style="margin-left: 50px; width: 350px; float: left;"> 
     {A} &nbsp; 
     {B} &nbsp;
     {C} &nbsp; 
     {D} 
     </div>
</div>
"""
