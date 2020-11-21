bokeh_template = """
	{% from macros import embed %}
	<!DOCTYPE html>
	<html lang="en">
	  {% block head %}

	    <!-- Bootstrap CSS -->
	    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
	       <!-- Optional JavaScript -->
	    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
	    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
	    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
	    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>

	  <script src="https://cdn.jsdelivr.net/npm/jstat@latest/dist/jstat.min.js"></script>
	  <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs/dist/tf.min.js" type="text/javascript"></script>
	  <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjs/7.6.0/math.min.js" type="text/javascript"></script>
	  
	  <script src="script.js" type="text/javascript"></script>
	  <link rel="stylesheet" href="style.css">

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

div_space = '<div style="width: {width}px; height: {height}px;"></div>'

#	<span style='text-align: center; font-size:50px;'>&nbsp;&#128170;&#127997;&#129299;</span>
div_conclusion = """
<div style="font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;">
<p class="text"> 
	Why did I go through the trouble to aggregate all this data from different devices and services?
	What's the point? Is this useful for anything besides flexing my data skills? 
	Well, to me this is a tool to help keep me motivated and accountable. Now that I have put 
	in so much effort into visualizing my data, I guess I have to keep working out to 
	produce more data to visualize... &#128170;&#127997;&#129299;
</p>
</div>
"""

div_workout_cal = """
<div style="font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;"> 
	<h2 class="h2">&#128197; Workout Calendar</h2>
	<p class="text"> 
		I try to workout Mon-Fri and rest on the weekends. I have tried the 3 days on and 2 days off
		pattern as well. Although I liked that pattern better, the 5 days on 2 days off pattern usually works best
		with my schedule. Most gyms are also on this pattern. The calendar plot below shows a heatmap of 
		calories burned on a given day. Hover over or tap a date to see details of the workout.
	</p>
</div>
"""

div_header = """
<div class="header" style="style=font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 400px; float: left;">
<h1 class="h1">Hasan Nagib</h1> 
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">

<a href="https://www.linkedin.com/in/hnagib?_l=en_US" target="_blank" class="fa fa-linkedin" style="font-size:24px"></a>
<a href="https://github.com/hnagib" class="fa fa-github" target="_blank" style="font-size:24px"></a>
<a href="https://www.facebook.com/bigannasah/" target="_blank" class="fa fa-facebook" style="font-size:24px"></a>
<a href="https://www.instagram.com/hnagib/" target="_blank" class="fa fa-instagram" style="font-size:24px"></a>
<a href="https://twitter.com/HasanNagib/" target="_blank" class="fa fa-twitter" style="font-size:24px"></a>
<a href="mailto:hasan.nagib@gmail.com?subject = Hasan's fitness data blog&body = Hello!" class="fa fa-envelope" style="font-size:24px"></a>
<a href="https://drive.google.com/file/d/1EknQPaDBVSqB5ABQFnoCiVADLD6bsKyY/view?usp=sharing" target="_blank" class="fa fa-file tooltip" style="font-size:24px">
<span class="tooltiptext">Resume</span></a>
"""

div_intro = """
<div style="font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;">
<p class="text">
    Welcome to my health & fitness data journal! This project was born out of my love for fitness, data & 
    <a href="https://docs.bokeh.org/en/latest/index.html" class="url" target="_blank">Bokeh</a>. The goal of this project is to aggregate and visualize 
    all of my health and fitness data from various sources. The data is sourced from my Fitbit, Polar HR10, Wahoo TickerX and 
    <a href="https://www.wodup.com" class="url" target="_blank">WodUp</a> account. 
</p>
"""

div_hr_rcvry = """
<div style="style=font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;"> 
<h2 class="h2">&#127939;&#127997; Workouts & Heart Rate</h2>
<p class="text">Heart rate recovery greater than 53 bpm in 2 minutes indicates that one's biological age 
is younger than calendar age. Greater recovery HR generally correlates with better health. Check out this 
<a href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5524096/#jah32178-sec-0016title" class="url" target="_blank">meta analysis</a> 
for more on this. The bar chart below shows my 2 minute recovery heart rate following workouts. 
This is calculated automatically using data collected from my Polar HR10 or Wahoo TickerX chest straps.   
Click on any bar to see corresponding workout and HR profile.
</p>
</div>
"""

# <p class="text">&nbsp;</p>
div_hr_zones = """
<div style="font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;">   
<p class="text">&nbsp;</p>
<p class="text">&nbsp;</p>
<p class="text">I also find it useful to monitor time spend in different HR zones. This can help guide my own programming 
and help me decide when to push hard or slow down in CrossFit classes. I generally aim to keep 7 day cumulative 
peak HR zone around or under 30-45 minutes depending on the goal of a given programming cycle. 
</p>
</div>
"""


div_hr_profile = """
<div style="font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;">   
<p class="text">
Heart rate data is sourced from <a class="url" target="_blank" href="https://www.polar.com/ca-en/products/accessories/h10_heart_rate_sensor">Polar HR10</a> 
and <a class="url" target="_blank" href="https://www.wahoofitness.com/devices/heart-rate-monitors/tickr-x/buy">Wahoo TickerX's</a> .fit files. 
The .fit files are synced to Dropbox from the Wahoo iOS app and 
parsed using the <a href="https://pypi.org/project/fitparse/" class="url" target="_blank">fitparse</a> python library.
</p>
</div>
"""


div_wod_logs="""
<div style="font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;">   
<h2 class="h2">&#128217; WOD Logs</h2>
<p class="text">I use <a href="https://www.wodup.com" class="url" target="_blank">WodUp</a> to log my workouts. Unfortunately WodUp currently does 
not have an API to retrieve this data. Workout logs are scraped from my <a href="https://www.wodup.com" class="url" target="_blank">WodUp</a> account 
using <a class="url" target="_blank" href="https://pypi.org/project/selenium/">selenium</a>. Pick a date to see the WOD and the corresponding HR profile. 
</p>
</div>
"""

div_weight_lifting = """
<div style="font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;"> 
<h2 class="h2">&#127947;&#127997; Weight Lifting</h2>
<p class="text">The views below show lift PRs for different movements and reps. 
I currently weigh ~165 lbs and my three lift total is {} lbs. 
In terms of <a href="https://strengthlevel.com/powerlifting-standards" class="url" target="_blank">powerlifting standards</a>,
I would be an intermediate lifter. My goal is to get to the advanced level (i.e. 1000 lbs) by end of 2021. 
I am hoping to get there with a 405 lbs deadlift, 355 lbs back squat & 240 lbs bench press &#129310;&#127997;
</p>
</div>
"""

# <p class="text">&nbsp;</p>
# <p class="text">&nbsp;</p>
div_lift_total = """
<div style="font-size:12px; font-family:helvetica; text-align: left;color:grey; margin-left: 40px; width: 400px; float: left;"> 
<h2 class="h2">
<span style="color:#154ba6">Bench</span> +
<span style="color:#3f8dff">Squat</span> + 
<span style="color:#7ec4ff">Deadlift</span> = 
<span style="color:#e73360">{}</span> lbs</h2>
</div"""

div_sleep = """
<div style="font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;">
<h2 class="h2">&#128564; Sleep Logs</h2>
<p class="text">
    Sleep data is sourced from <a href="https://www.fitbit.com/" class="url" target="_blank">Fitbit</a> sleep logs. 
    My goal is to average 7.5 hours of time asleep and 9 hours time in bed. The sleep quality plot shows different
    stages of sleep. Sleep start (bed time) and end (wake up time) hours are shown in the sleep schedule plot along with
    rolling average of last 7 days. 
</p>
</div>
"""

# <li>avg({x}) = {x_avg}</li>
# <li>avg({y}) = {y_avg}</li>

div_sleep_regression_desc = """
<div style="font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;">
<p>
Does sleeping in impact how much sleep I get the following day? Do I tend to get more sleep when I have a 
consistent bedtime and/or wake up time? Does consistent bedtime matter more than consistent wake up time? 
We can begin to explore these questions using the interactive regression tool! I used 
<a href="https://mathjs.org/" class="url" target="_blank">math.js</a> for the linear algebra 
and <a href="https://cdnjs.com/libraries/jstat" class="url" target="_blank">jstat</a> for p-value lookup. 
</p>
</div>
"""

div_sleep_plot = """
<div style="font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;">
<p class="text">
Select a subset of data using the box select tool from any of the plots here. 
This will trigger re-run of the regressions on the subset. The regression summary table will update accordingly.
This can useful for analyzing data from specific time periods or for filtering out unwanted data. e.g. If you choose 
X: start_hour and Y: end_hour from the dropdown widget, you can clearly see some outliers that are my rare naps. 
If we wanted to exclude these naps from the regression analysis, we could select the non-nap sleep logs from this view 
prior to choosing regression variables of interest.
"""

div_smry = """
<div style="font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;">
<h2 class="h2">&#128202;Summary</h2>
        <table class="table table-hover table-sm .table-bordered ">
          <thead>
            <tr>
              <th scope="col"></th>
              <th scope="col" style="text-align:center">coef</th>
              <th scope="col" style="text-align:center">std err</th>
              <th scope="col" style="text-align:center">t</th>
              <th scope="col" style="text-align:center">p > |t|</th>
              <th scope="col" style="text-align:center">[0.025</th>
              <th scope="col" style="text-align:center">0.975]</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="row" style="text-align:right">X</th>
              <td id="b1" style="text-align:center">{b1}</td>
              <td id="se_b1" style="text-align:center">{se_b1}</td>
              <td id="t_b1" style="text-align:center">{t_b1}</td>
              <td id="p_b1" style="text-align:center">{p_b1}</td>
              <td id="ci_025_b1" style="text-align:center">{ci_025_b1}</td>
              <td id="ci_975_b1" style="text-align:center">{ci_975_b1}</td>
            </tr>
            <tr>
              <th scope="row" style="text-align:right">const</th>
              <td id="b0" style="text-align:center">{b0}</td>
              <td id="se_b0" style="text-align:center">{se_b0}</td>
              <td id="t_b0" style="text-align:center">{t_b0}</td>
              <td id="p_b0" style="text-align:center">{p_b0}</td>
              <td id="ci_025_b0" style="text-align:center">{ci_025_b0}</td>
              <td id="ci_975_b0" style="text-align:center">{ci_975_b0}</td>
            </tr>
          </tbody>
        </table>
"""

div_sample_smry = """
<div style="font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 450px; float: left;">
        <table class="table table-hover table-sm ">
          <thead>
            <tr>
              <th scope="col" style="text-align:center">Sample size</th>
              <th scope="col" style="text-align:center">Selected</th>
              <th scope="col" style="text-align:center">avg(X)</th>
              <th scope="col" style="text-align:center">avg(Y)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td id="n_total" style="text-align:center">{n_total}</td>
              <td id="n_selected" style="text-align:center">{n_selected}</td>
              <td id="avg_x" style="text-align:center">{avg_x}</td>
              <td id="avg_y" style="text-align:center">{avg_y}</td>
            </tr>
          </tbody>
        </table>
"""

div_wodup = """
<div style="font-size:12px; font-family:helvetica; width: 100%; overflow: hidden;">
     <div style="margin-left: 50px; width: 350px; float: left;"> 
     {wod}
     </div>
</div>
"""

div_pr_cal_header = """
<h2 class="h2">Lift PR Calendar</h2>
"""

div_program = """
<h2 class="h2">Monday</h2>
    <ul>
        <li>Half kneeling landmine press</li>
        <li>Strict chin up</li>
        <li>Assault bike: Max cals in 10 minutes</li>
    </ul>
<h2 class="h2">Tuesday</h2>
    <ul>
        <li>Ring dips</li>
        <li>Nordic hamstring curls</li>
        <li>Box pistols 5x10</li>
        <li>Assault bike: Max cals in 15 minutes</li>
    </ul>
<h2 class="h2">Wednesday</h2>
    <ul>
        <li>Handstand push up</li>
        <li>Barbell hip thrust</li>
        <li>4 Rounds for time:</li>
            <ul>
                <li>4 Strict pull ups</li>
                <li>8 Burpees</li>
                <li>16 Box jumps</li>
                <li>32 Double Unders</li>
            </ul>
    </ul>
<h2 class="h2">Thursday</h2>
    <ul>
        <li>Ring muscle ups 10x5</li>
        <li>Handstand push ups 5x5</li>
        <li>Box pistols 5x10</li>
        <li>Assault bike: Max cals in 15 minutes</li>
    </ul>
<h2 class="h2">Friday</h2>
    <ul>
        <li>Nordic hamstring curls</li>
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

squatchek = """

<!DOCTYPE html>
<html lang="en">
{% block head %}
     <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- Import the webpage's stylesheet -->
    <link rel="stylesheet" href="style.css">
  	<!-- Load d3.js -->
    <script src="https://d3js.org/d3.v4.js"></script>

    <!-- Import TensorFlow.js library -->
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs/dist/tf.min.js" type="text/javascript"></script>
    <!-- Load the coco-ssd model to use to recognize things in images -->
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/coco-ssd"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/body-pix@2.0"></script>
    <script src="https://requirejs.org/docs/release/2.3.5/minified/require.js"></script>
    <!-- Import the page's JavaScript to do some stuff -->
    <script src="squatchek.js" defer></script>
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
    {% block contents %}
		    <h1>SquatCheck</h1>
		    <p>Squat form checking using TensorflowJS and Bodypix</p>
		    <button id="webcamButton">Enable Webcam</button>
		    
		    <div id="demos">
		      <div id="liveView" class="camView">
		        <canvas id="canvas" width="640" height="480" style="border:1px solid #ffffff;">
		          <video id="webcam" autoplay width="640" height="480"></video>
		        </canvas>
		      </div>
		    </div>
        {% for doc in docs %}
        {{ embed(doc) if doc.elementid }}
        {% for root in doc.roots %}
            {{ embed(root) | indent(10) }}
        {% endfor %}
        {% endfor %}
    {% endblock %}
    {{ plot_script | indent(8) }}
    {% endblock %}
</body>
{% endblock %}
</html>
"""
