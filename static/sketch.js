var activeAnimations = [];
var nextAnimations = [];

function setup() {
  var canv = createCanvas(windowWidth, windowHeight);
  canv.canvas.style['display'] = 'block';
  activeAnimations.push(new backgroundDarkenAnimation());
  activeAnimations.push(new textConstantAnimation('iQuestion'));
}

function draw() {
  processAnimations()
}


function processAnimations() {
  for(var anim of activeAnimations) {
    anim.run();
    if (anim.currentStep < anim.duration) {
      nextAnimations.push(anim);
    } else {
      anim.postmortem(nextAnimations);
    }
  }
  activeAnimations = nextAnimations;
  nextAnimations = [];
}

function backgroundDarkenAnimation() {
  this.brightnessRange = [255, 0];
  this.duration = 100;
  this.currentBrightness = 255;
  this.currentStep = 0;
  this.step = function() {
    brightnessStep = (this.brightnessRange[1] - this.brightnessRange[0]) / this.duration;
    this.currentBrightness = this.currentBrightness + brightnessStep;
    this.currentStep += 1;
  };
  this.run = function() {
    this.step();
    background(this.currentBrightness);
  };
  this.postmortem = function(newSeries) {
    newSeries.push(new backgroundConstantAnimation(this.currentBrightness));
  };

  return this;
}

function backgroundConstantAnimation(brightness) {
  this.duration = 1;
  this.currentStep = 0;
  this.currentBrightness = brightness;
  this.step = function() {

  };
  this.run = function() {
    background(this.currentBrightness);
  };
  this.postmortem = function(newSeries) {

  };
}

function textFadeAnimation(message, brightnessRange, ancestors) {
  this.message = message;
  this.align = CENTER;
  this.brightnessRange = brightnessRange;
  this.currentBrightness = this.brightnessRange[0];
  this.duration = 100;
  this.currentStep = 0;
  this.ancestors = ancestors;
  this.step = function() {
    brightnessStep = (this.brightnessRange[1] - this.brightnessRange[0]) / this.duration;
    this.currentBrightness = this.currentBrightness + brightnessStep;
    this.currentStep += 1;
  };
  this.run = function() {
    fill(this.currentBrightness);
    textSize(200);
    textFont(nanumBarunGothicFont);
    textAlign(this.align, this.align);
    text(this.message, 0, 0, windowWidth, windowHeight);
  };
  this.postmortem = function(newSeries) {
    newSeries.extend(this.ancestors);
  };
}

function textConstantAnimation(message, brightness) {
  this.message = message;
  this. 
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
}