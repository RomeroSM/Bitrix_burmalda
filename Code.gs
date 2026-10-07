function doPost(e) {
  var payload = JSON.stringify(e.parameters);
  Logger.log(payload);
  var ss = SpreadsheetApp.openById('1lFmsEk6acbGIiFgQhfk9iJq7KpA_4hLMZV0Rp7tRH8o');
  var sheet = ss.getSheetByName('log');
  var lastrow = sheet.getLastRow() + 1;
  var taskID = String(e.parameters.taskID);
  var elemID = String(e.parameters.elemID);
  if (e.parameters.portal != undefined) {
    var portal = 2;
  } else {
    var portal = 0;
  }
  var da = new Date();
  sheet.getRange(lastrow, 1).setValue(da);
  sheet.getRange(lastrow, 2).setValue(taskID);
  sheet.getRange(lastrow, 3).setValue(elemID);
  var chResult = getTaskChList(taskID, portal);
  sheet.getRange(lastrow, 4).setValue(chResult.state);
  sheet.getRange(lastrow, 5).setValue(chResult.title);
  if (chResult.state == true) {
    var st = elemUpdate(elemID, chResult.title, portal);
  }
  sheet.getRange(lastrow, 6).setValue(st);
}

function elemUpdate(elemID, sTitle, portal) {
  //elemID = '40411'
  //sTitle = 'testTitle'
  if (portal == 2) {
    var procID = '32';
  } else {
    var procID = '83';
  }
  var sRestMethod = 'lists.element.get';
  var oObject = {
    'IBLOCK_TYPE_ID': 'bitrix_processes',
    'IBLOCK_ID': procID,
    'ELEMENT_ID': elemID
  };
  var currentResult = getBitrix24Data(sRestMethod, oObject, portal);
  var oldObject = currentResult.result[0];
  for (var prop in oldObject) {
    if (typeof oldObject[prop] === 'object') {
      for (var key in oldObject[prop]) {
        if (typeof oldObject[prop][key] === 'object' && oldObject[prop][key].TYPE === 'HTML') {
          oldObject[prop] = oldObject[prop][key].TEXT;
        }
      }
    }
  }
  sRestMethod = 'lists.element.update';
  if (portal == 2) {
    oldObject.PROPERTY_258 = '556';
    oldObject.PROPERTY_260 = sTitle;
  } else {
    oldObject.PROPERTY_849 = '2437';
    oldObject.PROPERTY_851 = sTitle;
  }
  oObject = {
    'IBLOCK_TYPE_ID': 'bitrix_processes',
    'IBLOCK_ID': procID,
    'ELEMENT_ID': elemID,
    'FIELDS': oldObject
  };
  var result = getBitrix24Data(sRestMethod, oObject, portal);
  return result.result;
}

function getTaskChList(taskID, portal) {
  //taskID = '13349'
  var sRestMethod = 'task.checklistitem.getlist';
  var oObject = {
    'TASKID': taskID
  };
  var res = getBitrix24Data(sRestMethod, oObject, portal);
  var arr = res.result;
  var retObj = new Object();
  retObj.state = false;
  retObj.title = '';
  for (var i = 0; i < arr.length; i++) {
    if (arr[i].PARENT_ID != 0) {
      if (arr[i].TITLE == 'Запчасти') {
        if (arr[i].IS_COMPLETE == 'Y') {
          retObj.state = true;
        }
      } else {
        if (retObj.title == '') {
          retObj.title = arr[i].TITLE;
        } else {
          retObj.title = retObj.title + ', ' + arr[i].TITLE;
        }
      }
    }
  }
  return retObj;
}

function getBitrix24Data(sMethod, oData, portal) {
  if (portal == 2) {
    var hook = 'XXXXXXXXXXXXXXXX';
    var urlHook = 'https://coffeeteen.bitrix24.ru/rest/36/' + hook + '/' + sMethod + '.json';
  } else {
    var hook = 'XXXXXXXXXXXXXXXX';
    var urlHook = 'https://franshizasvezhar.bitrix24.ru/rest/667/' + hook + '/' + sMethod + '.json';
  }
  var options = {
    'method': 'get',
    'contentType': 'application/json',
    'payload': JSON.stringify(oData),
    'muteHttpExceptions': true
  };
  var response = UrlFetchApp.fetch(urlHook, options);
  var oString = response.getContentText();
  var oResult = JSON.parse(oString);
  return oResult;
}
