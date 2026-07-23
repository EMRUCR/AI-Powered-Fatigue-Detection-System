#include <Arduino.h>
#include <FastLED.h>

#define LED_PIN 18
#define NUM_LEDS 144
#define BRIGHTNESS 0

#define COLOR CRGB(0, 0, 255)
#define ORANGE_WARNING_COLOR CRGB(255, 85, 0)
#define RED_WARNING_COLOR CRGB(255, 0, 0)

CRGB leds[NUM_LEDS];

// red blinking
bool red_blink_active = false;
bool red_led_on = false;

unsigned long last_red_blink_time = 0;
const unsigned long RED_BLINK_INTERVAL = 460;

// functions
void openning_animation();
void normal_to_orange_warning();
void orange_to_red_warning();
void orange_to_normal_warning();
void red_to_normal_warning();

void setup()
{
  Serial.begin(115200);

  FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);

  Serial.println("LED testi basladi.");
}

void loop()
{
  if (Serial.available() > 0)
  {
    // read the command until the end of the line
    String command = Serial.readStringUntil('\n');

    // remove spaces and line ending characters
    command.trim();

    // run the corresponding function based on the received command
    if (command == "OPENING")
    {
      red_blink_active = false;
      red_led_on = false;

      openning_animation();
    }

    else if (command == "NORMAL_TO_ORANGE")
    {
      red_blink_active = false;
      red_led_on = false;

      normal_to_orange_warning();
    }

    else if (command == "ORANGE_TO_RED")
    {
      orange_to_red_warning();
    }

    else if (command == "ORANGE_TO_NORMAL")
    {
      red_blink_active = false;
      red_led_on = false;

      orange_to_normal_warning();
    }

    else if (command == "RED_TO_NORMAL")
    {
      red_blink_active = false;
      red_led_on = false;

      red_to_normal_warning();
    }

    else if (command == "NORMAL")
    {
      red_blink_active = false;
      red_led_on = false;

      fill_solid(leds, NUM_LEDS, COLOR);
      FastLED.show();
    }
  }

  // blink the red light while the alarm is active
  if (red_blink_active)
  {
    unsigned long current_time = millis();

    if (current_time - last_red_blink_time >= RED_BLINK_INTERVAL)
    {
      last_red_blink_time = current_time;

      red_led_on = !red_led_on;

      if (red_led_on)
      {
        fill_solid(leds, NUM_LEDS, RED_WARNING_COLOR);
      }

      else
      {
        fill_solid(leds, NUM_LEDS, CRGB(0, 0, 0));
      }

      FastLED.show();
    }
  }
}

// functions

void openning_animation()
{
  // quickly increase the brightness to one third of the maximum
  for (int i = 0; i < 85; i += 1)
  {
    fill_solid(leds, NUM_LEDS, COLOR);

    FastLED.setBrightness(BRIGHTNESS + i);
    FastLED.show();

    delay(80);
  }

  // wait for two seconds
  delay(2000);

  // increase the brightness faster after a short wait
  for (int i = 0; i < 170; i += 5)
  {
    fill_solid(leds, NUM_LEDS, COLOR);

    FastLED.setBrightness(85 + i);
    FastLED.show();

    delay(20);
  }
}

void orange_to_red_warning()
{
  // start the red blinking cycle
  red_blink_active = true;
  red_led_on = true;

  last_red_blink_time = millis();

  // turn on the first red light immediately
  fill_solid(leds, NUM_LEDS, RED_WARNING_COLOR);
  FastLED.show();
}

void red_to_normal_warning()
{
  red_blink_active = false;
  red_led_on = false;

  for (int i = 0; i < 255; i += 5)
  {
    fill_solid(leds, NUM_LEDS, COLOR);

    FastLED.setBrightness(BRIGHTNESS + i);
    FastLED.show();

    delay(20);
  }
}

void normal_to_orange_warning()
{
  fill_solid(leds, NUM_LEDS, COLOR);
  FastLED.show();

  int r = 0;
  int g = 0;
  int b = 255;

  for (int i = 0; i < 255; i += 3)
  {
    if (r + i <= 255 && g + (i / 3) <= 85 && b - i >= 0)
    {
      fill_solid(leds, NUM_LEDS, CRGB(r + i, g + (i / 3), b - i));
      FastLED.show();
      delay(10);
    }

    else
    {
      break;
    }
  }

  // keep the color fully orange
  fill_solid(leds, NUM_LEDS, ORANGE_WARNING_COLOR);
  FastLED.show();
}

void orange_to_normal_warning()
{
  fill_solid(leds, NUM_LEDS, ORANGE_WARNING_COLOR);
  FastLED.show();

  int r = 255;
  int g = 85;
  int b = 0;

  for (int i = 0; i < 255; i += 3)
  {
    if (r - i >= 0 && g - (i / 3) >= 0 && b + i <= 255)
    {
      fill_solid(leds, NUM_LEDS, CRGB(r - i, g - (i / 3), b + i));
      FastLED.show();
      delay(10);
    }

    else
    {
      break;
    }
  }

  // keep the color fully blue
  fill_solid(leds, NUM_LEDS, COLOR);
  FastLED.show();
}