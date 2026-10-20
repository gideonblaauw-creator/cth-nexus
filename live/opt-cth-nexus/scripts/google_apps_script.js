/**
 * Google Apps Script — Mentor Onboarding Form Trigger
 *
 * Deploy on the Google Sheet linked to the mentor registration Google Form.
 *
 * Setup:
 *   1. Open the response spreadsheet in Google Sheets
 *   2. Extensions > Apps Script
 *   3. Paste this file
 *   4. Set Script Properties (Project Settings > Script Properties):
 *        WEBHOOK_URL    = https://nexus.cleantechhub.net/mentor-api/onboard
 *        WEBHOOK_SECRET = <same value as WEBHOOK_SECRET in /opt/cth-nexus/.env>
 *   5. Add trigger: onFormSubmit → From spreadsheet → On form submit
 *
 * Column mapping:
 *   Edit the COLUMN_MAP below to match YOUR form's exact question text.
 *   Keys on the left are what the webhook expects; values on the right
 *   are the Google Form question titles (case-sensitive).
 */

// Maps webhook field names to form question titles.
// Adjust the right-hand strings to match your form exactly.
var COLUMN_MAP = {
  name:        "Nombre completo",
  email:       "Correo electrónico",
  phone:       "Teléfono / WhatsApp",
  linkedin:    "LinkedIn URL",
  company:     "Empresa actual",
  role:        "Cargo / Función actual",
  expertise:   "Área de expertise",
  programs:    "Programas CTH",
  bio:         "Bio breve",
  habeas_data: "Autorizo el tratamiento de datos personales",
};


function onFormSubmit(e) {
  var props = PropertiesService.getScriptProperties();
  var url    = props.getProperty("WEBHOOK_URL");
  var secret = props.getProperty("WEBHOOK_SECRET");

  if (!url) {
    Logger.log("ERROR: WEBHOOK_URL not set in script properties");
    return;
  }

  // Build payload from form response
  var responses = e.namedValues;  // { "Question Title": ["answer"], ... }
  var payload = { source: "google-form" };

  for (var field in COLUMN_MAP) {
    var question = COLUMN_MAP[field];
    var answer = responses[question];
    payload[field] = answer ? answer[0] : "";
  }

  // Fallback: if email came from Google Forms' built-in collector
  if (!payload.email && e.namedValues["Email Address"]) {
    payload.email = e.namedValues["Email Address"][0];
  }

  var body = JSON.stringify(payload);

  // HMAC-SHA256 signature
  var signature = "";
  if (secret) {
    var hmac = Utilities.computeHmacSha256Signature(body, secret);
    signature = hmac.map(function(b) {
      return ("0" + (b & 0xff).toString(16)).slice(-2);
    }).join("");
  }

  var options = {
    method: "post",
    contentType: "application/json",
    payload: body,
    headers: { "X-CTH-Signature": signature },
    muteHttpExceptions: true,
  };

  try {
    var response = UrlFetchApp.fetch(url, options);
    var code = response.getResponseCode();
    var text = response.getContentText();
    Logger.log("Webhook " + code + ": " + text);

    if (code >= 400) {
      // Tag the row for manual review
      _markRow(e, "WEBHOOK_ERROR " + code);
    }
  } catch (err) {
    Logger.log("Webhook failed: " + err);
    _markRow(e, "WEBHOOK_EXCEPTION");
  }
}


/**
 * Optional: write a status note in the last column of the response row.
 */
function _markRow(e, msg) {
  try {
    var sheet = e.range.getSheet();
    var row = e.range.getRow();
    var lastCol = sheet.getLastColumn() + 1;
    sheet.getRange(row, lastCol).setValue(msg + " " + new Date().toISOString());
  } catch (ignored) {}
}


/**
 * Manual test function — run from Apps Script editor to verify connectivity.
 * Sends a test payload; the webhook will reject habeas_data="test".
 */
function testWebhook() {
  var e = {
    namedValues: {},
    range: null,
  };
  // Simulate a form response
  for (var field in COLUMN_MAP) {
    var q = COLUMN_MAP[field];
    e.namedValues[q] = ["test"];
  }
  e.namedValues[COLUMN_MAP.email] = ["test-trigger@cleantechhub.net"];
  e.namedValues[COLUMN_MAP.name]  = ["Test Trigger"];
  e.namedValues[COLUMN_MAP.habeas_data] = ["acepto"];

  // Stub range
  e.range = SpreadsheetApp.getActiveSheet().getRange("A1");

  onFormSubmit(e);
}
