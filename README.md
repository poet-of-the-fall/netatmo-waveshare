# Netatmo Waveshare Display

This is a simple python project to show your Netatmo weather station data on a Waveshare epaper display.

![Example](https://raw.githubusercontent.com/poet-of-the-fall/netatmo-waveshare/refs/heads/main/images/example1.png)

It uses Pillow to compose an image that will then be shown on the display. It offers some classes making it easy to compose an image.

For autenticating to Netatmo and requesting data it uses [lnetatmo](https://github.com/philippelt/netatmo-api-python).

## Get it running

Check out the project with

```
git clone git@github.com:poet-of-the-fall/netatmo-waveshare.git
```

And also the submodules with

```
cd netatmo-waveshare
git submodule init
git submodule update
```

Install the dependecies with

```
pip3 install -r requirements.txt
```

If used on an rasperry pi directly you might also install some further required packages. Read the [Waveshare display](https://www.waveshare.com/wiki/Main_Page#Display-e-Paper) documentation on how to run the display with python.

Follow the steps in [lnetatmos usage description](https://github.com/philippelt/netatmo-api-python/blob/master/usage.md) to set up an App and your local credentials file. In short it's somethin like:

1. Visit [Netatmo Dev Portal](https://dev.netatmo.com/apps/createanapp#form) and create an app and some tokens with at least `read_station` scope.

2. Put those information in your local credentails file at `~/.netatmo.credentials` with the following content

```
{
    "CLIENT_ID" : "xxx",
    "CLIENT_SECRET" : "xxx",
    "REFRESH_TOKEN" : "xxx"
}
```

If ypou are NOT running this on a raspberry pi and just want to play around or compose your screens, check the `config.ini` and change `export_image` to `true`. Like this instead of triggering the screen you will get an image with the content.

Finally just run

```
./main.py
```

## Selecting display

To use the right lib for your display, just replace it in `main.py` in this section:

```
if not config.export_image:
    from waveshare_epd import epd7in5_HD as epd
    from waveshare_epd import epdconfig
```

Refere to the [Waveshare website](https://www.waveshare.com/wiki/Main_Page#Display-e-Paper) for more insigehts.

## Config

The config currently offers the following values.

In the general section:

| Parameter      | Default | Description                                                                                                                                          |
| -------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| log_level      | none    | Log level for the logger. Possibilities: none, debug, info, warning, error and critical                                                              |
| export_image   | false   | Saves an image instead of rendering to the display. Useful to compose the screen and when not having a device capable of running `python3-gpiozero`. |
| image_width    | 880     | Width of your Waveshare display.                                                                                                                     |
| image_height   | 528     | Height of your Waveshare display.                                                                                                                    |
| decimal_marker | ,       | Default decimal marker symbol.                                                                                                                       |

In the highlight section:

| Parameter    | Default | Description                                                                                                              |
| ------------ | ------- | ------------------------------------------------------------------------------------------------------------------------ |
| humidity_max | 60      | Max value for humidity. Higher values will invert the module representation to highlight a high value.                   |
| co2_max      | 2000    | Max value for CO2 ppm. Higher values will invert the module representation to highlight a high value.                    |
| battery_min  | 10      | Min value for battery charge state. Lower values will add a frame the module representation to highlight empty beteries. |
| calm_max     | 2       | Max wind speed for showing the calm icon (a central dot) instead of the angle indicator.                                 |
| wind_max     | 50      | Max wind speed. Higher values will invert the module representation to highlight a high value.                           |

## Craft your own layout

For desinging your own layout just edit the `main.py` file. It connects to Netatmo to request the data and uses some custom classes to compose the screens content called widgets.

Widgets define different layout mechanisms or data representations. All widgets functions return the widget itself so that it's easy to chain your layout definition (see later). The Following sections explain all the availabe widgets.

Widgets all have `View` as their parent class, so let`s first look at the parameters that are available for all the widgets.

### View (applies to all widgets)

The View is the base class for all widgets. So every widget hat the following functions:

| Function        | Parameters                     | Description                                                                                                                                                             |
| --------------- | ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| setSize         | width: int, height: int        | Sets the size of the view (will be calculated based on the available space if not set).                                                                                 |
| setHeight       | height: int                    | Sets the height of the view (will be calculated based on the available space if not set).                                                                               |
| setWidth        | width: int                     | Sets the width of the view (will be calculated based on the available space if not set).                                                                                |
| setPadding      | vertical: int, horizontal: int | Sets the padding for the view.                                                                                                                                          |
| setLayoutWeight | weight: int                    | Sets the weight four auto layout. If no width/height is set, the weight will be used for calculating the width/height of the view. Higher value will occupy more space. |
| setShowFrame    | show_frame: bool               | Toggle to draw a frame around the view.                                                                                                                                 |
| invert          | -                              | Will invert the views colors if called.                                                                                                                                 |

### Screen

Defines one screen containing all the widgets to be rendered to the display. It takes any other widget on its `.setView()` function to display. Use its `.render()` function to retrieve the image for showing on the screen.

| Function | Parameters | Description                |
| -------- | ---------- | -------------------------- |
| setView  | view: View | Adds a view to the screen. |

### HStack

This represents a horizontal layout composition. It takes one ore more views that will be put aside each other horizontally. It`s a basic view to help you layout your widgets on the display.

| Function | Parameters | Description                              |
| -------- | ---------- | ---------------------------------------- |
| addView  | view: View | Adds a view to the horizontal layout.    |
| setGap   | gap: int   | The gap between the views in the HStack. |

### VStack

This represents a vertical layout composition. It takes one ore more views that will be put aside each other vertically. It`s a basic view to help you layout your widgets on the display.

| Function | Parameters | Description                              |
| -------- | ---------- | ---------------------------------------- |
| addView  | view: View | Adds a view to the vertical layout.      |
| setGap   | gap: int   | The gap between the views in the VStack. |

### ZStack

This represents a overlaying layout composition. It takes one ore more views that will be put bovee each other. It`s a basic view to help you layout your widgets on the display. I used it for example to display a warning message when the Netatmo API is not reachable on top of the previous screen.

| Function | Parameters | Description                              |
| -------- | ---------- | ---------------------------------------- |
| addView  | view: View | Adds a view to the horizontal layout.    |
| setGap   | gap: int   | The gap between the views in the HStack. |

### Spacer

A Spacer is basic building block with no content. You can use it to fill up an area with white space next to another view. For example use it between two views with a defined width to fill the space between them as a spacer. Or before or after a view to move it to the bottom/rigth or top/left.

| Function | Parameters | Description                           |
| -------- | ---------- | ------------------------------------- |
| addView  | view: View | Adds a view to the overlaying layout. |

### Text Widget

This is a widget to display text. It will use the largest font possible if not set otherwise.

| Function               | Parameters                      | Description                                                                               |
| ---------------------- | ------------------------------- | ----------------------------------------------------------------------------------------- |
| setText                | text: str                       | Set the text to display.                                                                  |
| addTextLine            | text: str                       | Add another line if text if you need multiline text.                                      |
| setTextAlignHorizontal | text_align: TextAlignHorizontal | Define how the text should be aligned horizontally. Possibilities are: LEFT, CETER, RIGHT |
| setTextAlignVertical   | text_align: TextAlignVertical   | Define how the text should be aligned vertically. Pissobilities are: TOP, CENTER, BOTTOM  |
| setTextSize            | size: int                       | Define the exact text size.                                                               |
| setMaxTextSize         | size: int                       | Define a maximum text size.                                                               |

Constructor parameters:

| Parameter             | Type                | Mandatory | Default                                     |
| --------------------- | ------------------- | --------- | ------------------------------------------- |
| text                  | string              | yes       |                                             |
| text_align_horizontal | TextAlignHorizontal |           | TextAlignHorizontal.CENTER                  |
| text_align_vertical   | TextAlignVertical   |           | TextAlignVertical.CENTER                    |
| text_size             | integer             |           | None (will calculate maximum possible size) |
| max_text_size         | integer             |           | None                                        |

### Image Widget

A widget to show an image.

| Function    | Parameters      | Description                                     |
| ----------- | --------------- | ----------------------------------------------- |
| setImage    | image: Image    | The image to render.                            |
| setRotation | rotation: float | The angle by which the image should be rotated. |

Constructor parameters:

| Parameter | Type  | Mandatory | Default |
| --------- | ----- | --------- | ------- |
| image     | Image | yes       |         |
| rotation  | float |           | 0.0     |

### Module Widget

First complex widget showing a modules values. It is represented by a big central value with additional information above and below separated by a line.

| Function     | Parameters   | Description                                               |
| ------------ | ------------ | --------------------------------------------------------- |
| setHeader    | text: str    | Sets the header text.                                     |
| setBody      | text: str    | Sets the big body text.                                   |
| setFooter    | text: str    | Sets the footer text.                                     |
| setRatio     | ratio: float | Sets the ratio of the header and footer. Defaults to 0.2. |
| setUnit      | text: str    | Sets the unit for the body value,                         |
| setUnitRatio | ratio: float | Sets the ratio of the body unit. Defaults to 0.2.         |

Constructor parameters:

| Parameter  | Type   | Mandatory | Default |
| ---------- | ------ | --------- | ------- |
| header     | string |           | ""      |
| body       | string |           | ""      |
| footer     | string |           | ""      |
| ratio      | float  |           | 0.2     |
| unit       | string |           | None    |
| unit_ratio | float  |           | 0.2     |

This widget includes some special versions for different modules:

#### MainModuleWidget

Pass is the main module in the constructor and it will fill header, body and footer automatically with predefined values (humidity and CO2 in header, temperature in body and name in footer).

Constructor parameters:

| Parameter | Type                              | Mandatory | Default |
| --------- | --------------------------------- | --------- | ------- |
| module    | station data main module response | yes       |         |
| ratio     | float                             |           | 0.2     |

#### OutdoorModuleWidget

Pass is the outdoor module in the constructor and it will fill header, body and footer automatically with predefined values (humidity and mbar in header, temperature in body, name and update time in footer).

Constructor parameters:

| Parameter   | Type                                 | Mandatory | Default |
| ----------- | ------------------------------------ | --------- | ------- |
| module      | station data outdoor module response | yes       |         |
| main_module | station data main module response    | yes       |         |
| ratio       | float                                |           | 0.2     |

#### IndoorModuleWidget

Pass is any indoor module in the constructor and it will fill header, body and footer automatically with predefined values (humidity and CO2 in header, temperature in body and name in footer).

Constructor parameters:

| Parameter | Type                                 | Mandatory | Default |
| --------- | ------------------------------------ | --------- | ------- |
| module    | station data indoor mopdule response | yes       |         |
| ratio     | float                                |           | 0.2     |

#### RainModuleWidget

Pass is the rain module in the constructor and it will fill header, body and footer automatically with predefined values (when it last rained int he header, the rain of the current day in the body and the name in the footer).

Constructor parameters:

| Parameter      | Type                                        | Mandatory | Default |
| -------------- | ------------------------------------------- | --------- | ------- |
| module         | station data rain module response           | yes       |         |
| main_module    | station data main module response           | yes       |         |
| netatmo_client | WeatherStationData (the lnetatmo reference) | yes       |         |
| ratio          | float                                       |           | 0.2     |
| unit           | string                                      |           | mm      |
| unit_ratio     | float                                       |           | 0.2     |

#### WindModuleWidget

Pass is the wind module in the constructor and it will fill header, body and footer automatically with predefined values (current and max wind strenght in the header, current wind angle as indicator and history of the last 24h as image in the body and name in the footer).

Constructor parameters:

| Parameter      | Type                                        | Mandatory | Default |
| -------------- | ------------------------------------------- | --------- | ------- |
| module         | station data wind module response           | yes       |         |
| main_module    | station data main module response           | yes       |         |
| netatmo_client | WeatherStationData (the lnetatmo reference) | yes       |         |
| ratio          | float                                       |           | 0.2     |

### Graph Widget

A widget the prints the temperature as a graph. It can also contain the rain and a text for the day with min/max values.

| Function              | Parameters                | Description                                                                                                    |
| --------------------- | ------------------------- | -------------------------------------------------------------------------------------------------------------- |
| setDensity            | density: int              | Set the density of the graph, lower will show more days. It's basicly the pixels per half hour. Defaults to 4. |
| setShowDays           | show_days: bool           | Toggle showing the days underneath the graph (with min/max values if space for it).                            |
| setDayHeight          | day_height: int           | Sets height for the day text part. Defaults to 20.                                                             |
| setTempMin            | temp_min: int             | Sets the min temperature shown in the graph. Defaults to -10.                                                  |
| setTempMax            | temp_max: int             | Sets the max temperature shown in the graph. Defaults to 40.                                                   |
| setTempSteps          | temp_steps: int           | Sets the interval for the temperature indicators drwan on the y axis (left side). Defults to 10.               |
| setTempSize           | temp_size: int            | Sets the size for the temperature indicator values. Defaults to 10.                                            |
| setIndicatorSize      | indicator_size: int       | Sets the size of indicator line. Defaults to 3.                                                                |
| setLineWidth          | line_width: int           | Sets the line width of the temperature history. Defaults 1.                                                    |
| setCurrentValueRadius | current_value_radius: int | Sets the radius of the current value indicator, which is a dot at the end of the line. Defaults to 2.          |
| setHourTickInterval   | hour_tick_interval: int   | Sets the ticks of the hours on the x axis. Defaults to 6.                                                      |
| setRainModule         | rain_module               | Sets the rain module to show the rain bars for. Also toogles to show the rain bars if present.                 |
| setRainMax            | rain_max: int             | Sets the max rainfall shown in the graph per hour. Defaults to 10.                                             |
| setRainSteps          | rain_steps: int           | Sets the interval of the rain indicators drawn on the y axis (right side). Defaults to 10.                     |

Constructor parameters:

| Parameter            | Type                                        | Mandatory | Default |
| -------------------- | ------------------------------------------- | --------- | ------- |
| temperature_module   | station data module response                | yes       |         |
| main_module          | station data main module response           | yes       |         |
| netatmo_client       | WeatherStationData (the lnetatmo reference) | yes       |         |
| density              | integer                                     |           | 4       |
| show_days            | boolean                                     |           | True    |
| day_height           | integer                                     |           | 20      |
| temp_min             | integer                                     |           | -10     |
| temp_max             | integer                                     |           | 40      |
| temp_steps           | integer                                     |           | 10      |
| temp_size            | integer                                     |           | 10      |
| indicator_size       | integer                                     |           | 2       |
| line_width           | integer                                     |           | 1       |
| current_value_radius | integer                                     |           | 2       |
| hour_tick_interval   | integer                                     |           | 6       |
| rain_module          | station data rain module response           |           | None    |
| rain_max             | integer                                     |           | 10      |
| rain_steps           | integer                                     |           | 10      |
