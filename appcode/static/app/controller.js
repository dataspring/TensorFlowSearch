function getActiveStyle(styleName, object) {
  object = object || canvas.getActiveObject();
  if (!object) return '';

  return (object.getSelectionStyles && object.isEditing)
    ? (object.getSelectionStyles()[styleName] || '')
    : (object[styleName] || '');
}

function setActiveStyle(styleName, value, object) {
  object = object || canvas.getActiveObject();
  if (!object) return;

  if (object.setSelectionStyles && object.isEditing) {
    var style = { };
    style[styleName] = value;
    object.setSelectionStyles(style);
    object.setCoords();
  }
  else {
    object[styleName] = value;
  }

  object.setCoords();
  canvas.renderAll();
}

function getActiveProp(name) {
  var object = canvas.getActiveObject();
  if (!object) return '';
  return object[name] || '';
}

function setActiveProp(name, value) {
  var object = canvas.getActiveObject();
  if (!object) return;
  object.set(name, value).setCoords();
  canvas.renderAll();
}



function addAccessors($scope) {

  $scope.getOpacity = function() {
    return getActiveStyle('opacity') * 100;
  };
  $scope.setOpacity = function(value) {
    setActiveStyle('opacity', parseInt(value, 10) / 100);
  };

  $scope.getScale = function() {
    return (getActiveStyle('scaleX')+getActiveStyle('scaleY')) * 50;
  };
  $scope.setScale = function(value) {
    setActiveStyle('scaleX', parseInt(value, 10) / 100);
    setActiveStyle('scaleY', parseInt(value, 10) / 100);
  };

  $scope.confirmClear = function() {
    if (confirm('Remove everything including images. Are you sure?')) {
      canvas.clear();
    }
  };

  $scope.confirmClearMasks = function() {
    if (confirm('Remove all masks. Are you sure?')) {
        canvas.forEachObject(function(obj){
            if (!obj.isType('image')){
                obj.remove()
            }
        });
    state.masks_present = false;
    }
  };

  $scope.showTour = function(){
      hopscotch.startTour(tour);
  };

  $scope.showDev = function(){
      $scope.dev = !$scope.dev;
  };

  $scope.getDev = function(){
      return $scope.dev
  };

  $scope.getConvnet = function(){
      return $scope.convnet_mode
  };

  $scope.getFill = function() {
    return getActiveStyle('fill');
  };
  $scope.setFill = function(value) {
    setActiveStyle('fill', value);
  };

  $scope.getBgColor = function() {
    return getActiveProp('backgroundColor');
  };
  $scope.setBgColor = function(value) {
    setActiveProp('backgroundColor', value);
  };


  $scope.getStrokeColor = function() {
    return getActiveStyle('stroke');
  };
  $scope.setStrokeColor = function(value) {
    setActiveStyle('stroke', value);
  };

  $scope.getStrokeWidth = function() {
    return getActiveStyle('strokeWidth');
  };
  $scope.setStrokeWidth = function(value) {
    setActiveStyle('strokeWidth', parseInt(value, 10));
  };

  $scope.getCanvasBgColor = function() {
    return canvas.backgroundColor;
  };

  $scope.setCanvasBgColor = function(value) {
    canvas.backgroundColor = value;
    canvas.renderAll();
  };





  $scope.getSelected = function() {
    return canvas.getActiveObject() || canvas.getActiveGroup();
  };

  $scope.removeSelected = function() {
    var activeObject = canvas.getActiveObject(),
        activeGroup = canvas.getActiveGroup();
    if (activeGroup) {
      var objectsInGroup = activeGroup.getObjects();
      canvas.discardActiveGroup();
      objectsInGroup.forEach(function(object) {
        canvas.remove(object);
      });
    }
    else if (activeObject) {
      canvas.remove(activeObject);
    }
  };

    $scope.resetZoom = function(){
        var newZoom = 1.0;
        canvas.absolutePan({x:0,y:0});
        canvas.setZoom(newZoom);
        state.recompute = true;
        renderVieportBorders();
        console.log("zoom reset");
        return false;
    };


  $scope.sendBackwards = function() {
    var activeObject = canvas.getActiveObject();
    if (activeObject) {
      canvas.sendBackwards(activeObject);
    }
  };

  $scope.sendToBack = function() {
    var activeObject = canvas.getActiveObject();
    if (activeObject) {
      canvas.sendToBack(activeObject);
    }
  };

  $scope.bringForward = function() {
    var activeObject = canvas.getActiveObject();
    if (activeObject) {
      canvas.bringForward(activeObject);
    }
  };

  $scope.bringToFront = function() {
    var activeObject = canvas.getActiveObject();
    if (activeObject) {
      canvas.bringToFront(activeObject);
    }
  };

  function initCustomization() {
    if (/(iPhone|iPod|iPad)/i.test(navigator.userAgent)) {
      fabric.Object.prototype.cornerSize = 30;
    }
    fabric.Object.prototype.transparentCorners = false;
    if (document.location.search.indexOf('guidelines') > -1) {
      initCenteringGuidelines(canvas);
      initAligningGuidelines(canvas);
    }
  }
  initCustomization();



  $scope.getFreeDrawingMode = function(mode) {
      if (mode){
        return canvas.isDrawingMode == false || mode != $scope.current_mode ? false : true;
      }
      else{
          return canvas.isDrawingMode
      }

  };

//mover_cursor = function(options) {yax.css({'top': options.e.y + delta_top,'left': options.e.x + delta_left});};


  $scope.setFreeDrawingMode = function(value,mode) {
    canvas.isDrawingMode = !!value;
    canvas.freeDrawingBrush.color = mode == 1 ? 'green': 'red';
    if (value && mode == 1){
        $scope.status = "Highlight regions of interest"
    }else if(value){
        $scope.status = "Highlight regions to exclude"
    }
    if(canvas.isDrawingMode){
        //yax.show();
        //canvas.on('mouse:move',mover_cursor);
    }
   else{
        //yax.hide();
        //canvas.off('mouse:move',mover_cursor);
    }
    canvas.freeDrawingBrush.width = 5;
    $scope.current_mode = mode;
    canvas.deactivateAll().renderAll();
    $scope.$$phase || $scope.$digest();
  };

  $scope.freeDrawingMode = 'Pencil';

  $scope.getDrawingMode = function() {
    return $scope.freeDrawingMode;
  };

  $scope.setDrawingMode = function(type) {
    $scope.freeDrawingMode = type;
    $scope.$$phase || $scope.$digest();
  };

  $scope.getDrawingLineWidth = function() {
    if (canvas.freeDrawingBrush) {
      return canvas.freeDrawingBrush.width;
    }
  };

  $scope.setDrawingLineWidth = function(value) {
    if (canvas.freeDrawingBrush) {
      canvas.freeDrawingBrush.width = parseInt(value, 10) || 1;
    }
  };

  $scope.getDrawingLineColor = function() {
    if (canvas.freeDrawingBrush) {
      return canvas.freeDrawingBrush.color;
    }
  };
  $scope.setDrawingLineColor = function(value) {
    if (canvas.freeDrawingBrush) {
      canvas.freeDrawingBrush.color = value;
    }
  };


  $scope.duplicate = function(){
    var obj = fabric.util.object.clone(canvas.getActiveObject());
        obj.set("top", obj.top+12);
        obj.set("left", obj.left+9);
        canvas.add(obj);
  };


  $scope.load_image = function(){
    var input, file, fr, img;
    state.recompute = true;
    input = document.getElementById('imgfile');
    input.click();
  };

$scope.updateCanvas = function () {
    fabric.Image.fromURL(output_canvas.toDataURL('png'), function(oImg) {
        canvas.add(oImg);
    });
};


$scope.deselect = function(){
    canvas.deactivateAll().renderAll();
    $scope.$$phase || $scope.$digest();
};







$scope.refreshData = function(){
    if (state.recompute){
        canvas.deactivateAll().renderAll();
        canvas.forEachObject(function(obj){
            if (!obj.isType('image')){
                obj.opacity = 0;
            }
        });
        canvas.renderAll();
        state.canvas_data = canvas.getContext('2d').getImageData(0, 0, height, width);
    }
    else{
        console.log("did not recompute")
    }
    canvas.forEachObject(function(obj){
        if (!obj.isType('image')){
            obj.opacity = 1.0;
        }
        else{
            obj.opacity = 0;
        }
    });
    canvas.renderAll();
    state.mask_data = canvas.getContext('2d').getImageData(0, 0, height, width);
    canvas.forEachObject(function(obj){
        if (obj.isType('image'))
        {
            obj.opacity = 1.0;
        }
        else{
            obj.opacity = 1.0;
        }
    });
    canvas.renderAll();
};


$scope.checkTagContentType = function(){
    return $scope.tagContentType;
}

$scope.checkTagApprops = function(){
    return $scope.tagApprops;
}

$scope.checkStatus = function(){
    return $scope.status;
};

$scope.checkTagStatus = function(){
    return $scope.tagStatus;
}

$scope.disableStatus = function(){
    $scope.status = "";
};

$scope.disableTagStatus = function(){
    $scope.tagStatus = "";
};

$scope.check_movement = function(){
    // set image positions or check them
    if ($scope.dev){
        // Always recompute if dev mode is enabled.
        state.recompute = true;
    }
    canvas.forEachObject(function(obj){
        if (!obj.isType('image')){
            state.masks_present = true;
        }
    });
    old_positions_joined = state.images.join();
    state.images = [];
    canvas.forEachObject(function(obj){
        if (obj.isType('image')){
            state.images.push([obj.scaleX,obj.scaleY,obj.top,obj.left,obj.opacity])
        }
    });
    if(!state.recompute) // if recompute is true let it remain true.
    {
        state.recompute = state.images.join() != old_positions_joined;
    }
};

function chunk(arr, size) {
  var newArr = [];
  for (var i=0; i<arr.length; i+=size) {
    newArr.push(arr.slice(i, i+size));
  }
  return newArr;
}

$scope.search_quick = function () {
    $scope.setFreeDrawingMode(false,$scope.current_mode);
    $scope.check_movement();
    var a = performance.now();
    $scope.results = [];
    $scope.status = "Starting Quick Search";
    $scope.tagStatus = "Starting Image Content Analaysis";
    $scope.tagApprops = "";
    $scope.tagContentType = "";

    if(canvas.isDrawingMode){
        canvas.isDrawingMode = false;
        canvas.deactivateAll().renderAll();
    }
    $scope.$$phase || $scope.$digest();
    $scope.refreshData();

    $.ajax({
        type: "POST",
        url: '/Quick',
        dataType: 'json',
        async: true,
        data: {
            'image_url': canvas.toDataURL()
        },
        success: function (response) {
            var b = performance.now();
            //$scope.status = "Approximate Search Completed";
            $scope.status = "Approx. Search Completed in " + Math.round((b - a),4) + " ms.";
            $scope.results = chunk(response.results, 4);
            $scope.$$phase || $scope.$digest();

        }
    });

    tagUsingClarifai($scope, "Appropriate-ness" );
    tagUsingClarifai($scope, "Tag" );


};


function tagUsingClarifai($scope, tagType){
    
    var token;

    var a = performance.now();

    var clientData = {
        'grant_type': 'client_credentials',
        'client_id': '',
        'client_secret': ''
    };

    if (tagType === "Appropriate-ness") {
         //ecomSite-Nfsw
         clientData.client_id = 'ESXuZtuhlwIq8moJYmb6FX5TzL9_7S1fCvUg6XgH';
         clientData.client_secret = 'YjPWvx-qInXfRhOpg-bM77mAE1nqBiooclRofxZZ';
    }
    else {
        //ecomSite-General
        clientData.client_id = 'Aogy1PlggSYoke2gz8VEgEnk4UIwVJDch0gj4BQz';
        clientData.client_secret =  'URXHlJ3b9b-tfaEp57sDmqOQmgNXkJzFPCmAsEay';
    }
    
    var fileData = new FormData();
    fileData.append('encoded_data', canvas.toDataURL().slice(22));

    $.ajax({
        url: 'https://api.clarifai.com/v1/token',
        data: clientData,
        type: 'POST',
        async: true,
        success: function (response) {
            console.log("Obtained token response from Clarifai");
            //console.log("Token = " + response.access_token);
            //------------------- do an async call to Calrifai
            $.ajax({
                  url: 'https://api.clarifai.com/v1/tag/',
                  headers: {
                      'Authorization': 'Bearer ' + response.access_token,
                      //'Content-Transfer-Encoding' : 'base64'
                  },
                  //contentType: 'multipart/form-data',
                  processData: false,
                  contentType: false,                  
                  data: fileData,
                  type: 'POST',
                  async: true,
                  success: function (response) {
                      // ----------------- process once response arrives from image service ----
                      console.log(response);
                      console.log("Obtained response from Clarifai Service 2");
                      var b = performance.now();

                      if ($scope.tagStatus === "Starting Image Content Analaysis") {
                          $scope.tagStatus = "";
                      }

                      if (tagType === "Appropriate-ness") {
                         parseResponseForApprops(response);
                         $scope.tagStatus = $scope.tagStatus + " " + "Approp in " + Math.round((b - a),4) + " ms.";
                         $scope.$apply(); 
                      }
                      else {
                        parseResponseForTags(response);    
                        $scope.tagStatus = $scope.tagStatus + " " + "Tags in " + Math.round((b - a),4) + " ms.";
                        $scope.$apply();
                      }
                      // ----------------- routine ends here -----------------------------------
                  }
              });
        }
    });
}


function  parseResponseForTags(r) {
    var tagJson = {"tagresult":false, "classes":[], "probs": []}

    if (r.status_code === 'OK') {
        var results = r.results;
        tagJson.tagresult = true;
        tagJson.classes = results[0].result.tag.classes.slice(0,5);
        tagJson.probs = results[0].result.tag.probs.slice(0,5);
        $scope.tagContentType = 'Image Tags : ' + tagJson.classes.join();
        $scope.$apply(); 
    } 
    else {
        console.log('Sorry, something is wrong.');
    }
    //$('#tags').text(JSON.stringify(tagJson));
    //return tagJson;
} 

function parseResponseForApprops(r){
  
    var tagJson = {"tagresult":false, "sfw":false, "nsfw": false, "sfwProb":0, "nsfwProb":0}

    if (r.status_code === 'OK') {
        var results = r.results;
        tags = results[0].result.tag.classes;
        tagValues = results[0].result.tag.probs;

        tagJson.tagresult = true;
        tagJson.sfwProb = tagValues[0];
        tagJson.nsfwProb = tagValues[1];
        tagJson.sfw = (tagJson.sfwProb > 0.7) ? true : false;
        tagJson.nsfw = (tagJson.nsfwProb > 0.7) ? true : false; 
 
        $scope.tagApprops = 'Content Screened : ' + (tagJson.sfw ? 'Appropriate' : 'InAppropriate') + ',  Approp Prob : ' + tagJson.sfwProb.toString().slice(0,5)  + ' InApprop Prob : ' + tagJson.nsfwProb.toString().slice(0,5);
        $scope.tagAppropClass = tagJson.sfw ? 'w3-noteapp' : 'w3-noteinapp' 
        $scope.$apply();

    } else {
        console.log('Sorry, something is wrong.');
    }
    //$('#tags').text(JSON.stringify(tagJson));
    //return tagJson;  
}


$scope.search = function () {
    $scope.setFreeDrawingMode(false,$scope.current_mode);
    $scope.check_movement();
    var a = performance.now();
    $scope.results = [];
    $scope.status = "Starting Exact Search can take up to a minute";
    $scope.tagStatus = "Starting Image Content Analaysis";
    $scope.tagApprops = "";
    $scope.tagContentType = "";

    if(canvas.isDrawingMode){
        canvas.isDrawingMode = false;
        canvas.deactivateAll().renderAll();
    }
    $scope.$$phase || $scope.$digest();
    $scope.refreshData();
    $.ajax({
        type: "POST",
        url: '/Search',
        dataType: 'json',
        async: true,
        data: {
            'image_url': canvas.toDataURL()
        },
        success: function (response) {
            var b = performance.now();
            $scope.status = "Exact Search Completed in " + Math.round((b - a),4) + " ms.";
            $scope.results = chunk(response.results, 4);
            $scope.$$phase || $scope.$digest();

        }
    });
        tagUsingClarifai($scope, "Appropriate-ness" );
    tagUsingClarifai($scope, "Tag" );
};

}

function watchCanvas($scope) {

  function updateScope() {
    $scope.$$phase || $scope.$digest();
    canvas.renderAll();
  }

  canvas
    .on('object:selected', updateScope)
    .on('group:selected', updateScope)
    .on('path:created', updateScope)
    .on('selection:cleared', updateScope);
}



cveditor.controller('CanvasControls', function($scope) {
    $scope.convnet_mode = false;
    $scope.yax = $('#yaxis');
    $scope.canvas = canvas;
    $scope.output_canvas = output_canvas;
    $scope.getActiveStyle = getActiveStyle;
    $scope.dev = false;
    $scope.status = "Please add image.";
    $scope.tagStatus = "Image content will be analyzed for appropriate-ness.";
    $scope.tagApprops = "Content Appropriate-ness: To be determined";
    $scope.tagContentType = "Tags: To be determined";    
    $scope.tagAppropClass = 'w3-note';
    $scope.current_mode = null;
    $scope.results = [];
    addAccessors($scope);
    watchCanvas($scope);
});
