var socket = io.connect('http://' + document.domain + ":" + location.port);
var timer = document.getElementById('timer');
var canvas = document.getElementById('drawingCanvas');
var ctx = canvas.getContext('2d');
var clearbtn = document.getElementById('clearbtn');
var isDrawing = false;
var prevX = 0;
var prevY = 0;
var lineWidth = 3;

ctx.lineCap = 'round';

var drawLine = function(x0, y0, x1, y1, sendBack = true, inputWidth = lineWidth) {
  ctx.lineWidth = inputWidth;
  ctx.beginPath();
  ctx.moveTo(x0, y0); //Offset x and y by vector
  ctx.lineTo(x1, y1); //Draw line to center of the next circle
  ctx.stroke();
  if (sendBack) {
    socket.emit('newLine', [x0, y0, x1, y1, inputWidth]);
  }
}

var clearBoard = function(sendBack = true) {
  ctx.clearRect(0,0,canvas.width,canvas.height); //Clears the entire canvas
  if (sendBack) {
    socket.emit('clearBoard', null);
  }
}

socket.on('connect', function() { //Executed upon opening the site
  console.log('Successfully Connected');
  socket.emit('joinRoom', 'General'); //Automatically join General
  socket.emit('requestLines', null);
});

socket.on('recieveLines', function(lines) {
  for (var i = 0; i < lines.length; i += 1) {
    currLine = lines[i];
    drawLine(currLine[0], currLine[1], currLine[2], currLine[3], sendBack = false, inputWidth = currLine[4]);
  }
});

socket.on('newLine', function(line) {
  // console.log(line);
  drawLine(line[0], line[1], line[2], line[3], sendBack = false, inputWidth = line[4]);
});

socket.on('clearBoard', function(data) {
  clearBoard(sendBack = false);
});

socket.on('updateTimer', function(newTime) {
  timer.innerHTML = newTime;
});

canvas.addEventListener('mousedown', function(e) {
  prevX = e.offsetX;
  prevY = e.offsetY;
  isDrawing = true;
  drawLine(prevX, prevY, prevX, prevY);
});

canvas.addEventListener('mousemove', function(e) {
  if (isDrawing) {
    //Draw the line
    drawLine(prevX, prevY, e.offsetX, e.offsetY);
    prevX = e.offsetX;
    prevY = e.offsetY;
  }
});

canvas.addEventListener('mouseout', function(e) {
  isDrawing = false;
});

canvas.addEventListener('mouseup', function(e) {
  isDrawing = false;
});

canvas.addEventListener("wheel", function(e) {
  var change;
  if (e.deltaY > 0) {
    change = -1;
  } else {
    change = 1;
  }
  lineWidth += change;
  //console.log(lineWidth);
  if (lineWidth < 3) { //Clamp min brush size to 3 pixels
    lineWidth = 3;
  } else if (lineWidth > 20) { //Clamp max brush size to 20 pixels
    lineWidth = 20;
  }
  e.preventDefault(); //Prevent user from scrolling down the page
});
