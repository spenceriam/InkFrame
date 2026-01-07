# Web Interface Improvements - Implementation Plan

**Created:** January 7, 2026 at 14:30 UTC  
**Last Updated:** January 7, 2026  
**Related Issue:** N/A  
**Target Version:** 1.2.0  
**Branch:** `web-interface-improvements`  
**Status:** Planning

---

## Overview

This plan modernizes the InkFrame web settings interface to properly support the weather.gov API transition completed in v1.1.0. The current UI still contains obsolete OpenWeatherMap fields (API key, country code) that are no longer used. This update removes those fields, adds a Leaflet map-based location picker for precise coordinate selection, and streamlines the weather configuration workflow.

### Goals

1. Remove obsolete OpenWeatherMap configuration fields
2. Add interactive map-based location picker (inspired by eazyweather)
3. Support ZIP code text search as alternative to map
4. Maintain IP geolocation as fallback
5. Auto-migrate existing city/state configs to coordinates
6. Keep temperature units and timezone settings

### Version Impact

- **Type:** MINOR version bump (new features, backwards compatible)
- **Current:** 1.1.1
- **Target:** 1.2.0

---

## Architecture Overview

### Current Flow (v1.1.1)
```
User enters city/state/country/API key → Config saved → Weather client geocodes city/state → weather.gov API called
```

### New Flow (v1.2.0)
```
User picks location on map OR enters ZIP code → Coordinates saved → Weather client uses coordinates directly → weather.gov API called
```

### Key Files

| File | Purpose | Changes Required |
|------|---------|------------------|
| `static/templates/index.html` | Settings UI HTML | Remove obsolete fields, add map modal |
| `static/js/app.js` | Settings JavaScript | Add map picker logic, update validation |
| `static/css/styles.css` | UI Styling | Add map modal styles |
| `src/web/app.py` | Flask API endpoints | Update config handling |
| `src/utils/config_manager.py` | Config persistence | Add lat/lon fields |
| `config/default_config.json` | Default configuration | Update weather schema |
| `src/weather/weather_client.py` | Weather data fetching | Prioritize stored coordinates |
| `src/version.py` | Version info | Bump to 1.2.0 |
| `AGENTS.md` | Agent documentation | Add v1.2.0 history |

---

## Task Breakdown

### Phase 1: Configuration Schema Updates

#### Task 1.1: Update Default Configuration Schema

**Prerequisites:** None  
**Estimated Effort:** Small  
**Files:** `config/default_config.json`

**Context:**
The current weather config schema contains obsolete OpenWeatherMap fields. The weather.gov API doesn't require an API key and only works for US locations (making country code irrelevant).

**Current Schema:**
```json
"weather": {
  "api_key": "",
  "city": "",
  "state": "",
  "country": "",
  "units": "imperial",
  "update_interval_minutes": 30,
  "cache_expiry_minutes": 120
}
```

**Target Schema:**
```json
"weather": {
  "latitude": null,
  "longitude": null,
  "location_name": "",
  "city": "",
  "state": "",
  "units": "imperial",
  "update_interval_minutes": 30,
  "cache_expiry_minutes": 120
}
```

**Changes:**
1. Remove `api_key` field (not needed for weather.gov)
2. Remove `country` field (weather.gov is US-only)
3. Add `latitude` field (float or null)
4. Add `longitude` field (float or null)
5. Add `location_name` field (for display purposes, e.g., "Chicago, IL")
6. Keep `city` and `state` for backwards compatibility during migration

**Acceptance Criteria:**
- [ ] `default_config.json` updated with new schema
- [ ] No `api_key` field present
- [ ] No `country` field present
- [ ] `latitude`, `longitude`, `location_name` fields added

---

#### Task 1.2: Update Config Manager

**Prerequisites:** Task 1.1  
**Estimated Effort:** Small  
**Files:** `src/utils/config_manager.py`

**Context:**
The config manager handles loading, saving, and providing defaults for configuration. It needs to handle the new coordinate fields and provide migration logic for existing configs.

**Changes:**
1. Update default weather config to match new schema
2. Add migration logic: if `latitude`/`longitude` are missing but `city`/`state` exist, flag for geocoding
3. Remove any API key handling/masking logic
4. Add helper methods for coordinate validation

**Implementation Notes:**
- Coordinates should be validated as valid lat (-90 to 90) and lon (-180 to 180)
- Migration should be non-destructive (keep city/state for reference)
- Add `needs_location_migration()` method to check if geocoding needed

**Acceptance Criteria:**
- [ ] Default config includes new coordinate fields
- [ ] Migration detection logic implemented
- [ ] Coordinate validation helper added
- [ ] API key references removed

---

### Phase 2: Backend API Updates

#### Task 2.1: Update Flask Config Endpoint

**Prerequisites:** Task 1.2  
**Estimated Effort:** Medium  
**Files:** `src/web/app.py`

**Context:**
The `/api/config` endpoint currently accepts and masks `api_key`. It needs to accept coordinates directly and handle the new schema.

**Current Behavior:**
- GET `/api/config`: Returns config with masked API key
- POST `/api/config`: Accepts city, state, country, api_key, units

**Target Behavior:**
- GET `/api/config`: Returns config (no API key to mask)
- POST `/api/config`: Accepts latitude, longitude, location_name, city, state, units

**Changes:**
1. Remove API key masking from GET response
2. Update POST handler to accept coordinate fields
3. Add coordinate validation before saving
4. Keep accepting city/state for text-based search fallback

**Acceptance Criteria:**
- [ ] GET `/api/config` no longer references api_key
- [ ] POST `/api/config` accepts latitude, longitude, location_name
- [ ] Coordinate validation prevents invalid values
- [ ] City/state still accepted for fallback

---

#### Task 2.2: Add Geocoding API Endpoint

**Prerequisites:** Task 2.1  
**Estimated Effort:** Medium  
**Files:** `src/web/app.py`

**Context:**
To support ZIP code and text-based location search, we need an endpoint that geocodes text input to coordinates. This uses Nominatim (OpenStreetMap) which is already used in `weather_client.py`.

**New Endpoint:**
```
POST /api/location/geocode
Body: { "query": "60050" } or { "query": "Chicago, IL" }
Response: {
  "success": true,
  "results": [
    {
      "latitude": 42.3334,
      "longitude": -88.2826,
      "display_name": "McHenry, McHenry County, Illinois, USA"
    }
  ]
}
```

**Implementation Notes:**
- Use Nominatim API (same as weather_client.py)
- Limit results to US locations (countrycodes=us)
- Return multiple results for ambiguous queries
- Include proper User-Agent header (Nominatim requirement)
- Add rate limiting (1 request per second for Nominatim)

**Acceptance Criteria:**
- [ ] New `/api/location/geocode` endpoint created
- [ ] Accepts ZIP code and city/state queries
- [ ] Returns multiple results for ambiguous queries
- [ ] Proper error handling for failed geocoding
- [ ] Rate limiting implemented

---

#### Task 2.3: Add Reverse Geocoding Endpoint

**Prerequisites:** Task 2.2  
**Estimated Effort:** Small  
**Files:** `src/web/app.py`

**Context:**
When user places a pin on the map, we need to convert coordinates back to a readable location name for display.

**New Endpoint:**
```
POST /api/location/reverse
Body: { "latitude": 42.3334, "longitude": -88.2826 }
Response: {
  "success": true,
  "location_name": "McHenry, IL",
  "full_address": "McHenry, McHenry County, Illinois, 60050, USA"
}
```

**Implementation Notes:**
- Use Nominatim reverse geocoding
- Extract city/state for concise display name
- Include full address for tooltip/details
- Same rate limiting as forward geocoding

**Acceptance Criteria:**
- [ ] New `/api/location/reverse` endpoint created
- [ ] Returns formatted location name
- [ ] Proper error handling for invalid coordinates
- [ ] Rate limiting shared with geocoding endpoint

---

### Phase 3: Weather Client Updates

#### Task 3.1: Update Weather Client to Use Stored Coordinates

**Prerequisites:** Task 1.2  
**Estimated Effort:** Medium  
**Files:** `src/weather/weather_client.py`

**Context:**
Currently the weather client has a location detection flow:
1. Geocode city/state from config
2. IP geolocation fallback
3. Hardcoded default (McHenry, IL)

The new flow should prioritize stored coordinates:
1. **Use stored latitude/longitude if present**
2. Geocode city/state from config (for migration)
3. IP geolocation fallback
4. Hardcoded default (McHenry, IL)

**Changes:**
1. Add check for stored coordinates at start of `_get_coordinates()`
2. If coordinates exist and are valid, use them directly
3. If coordinates missing but city/state exist, geocode and optionally save coordinates
4. Update logging to indicate coordinate source

**Acceptance Criteria:**
- [ ] Stored coordinates are used when present
- [ ] Geocoding only runs if coordinates missing
- [ ] IP geolocation remains as fallback
- [ ] Logging indicates which method was used

---

### Phase 4: Frontend - Remove Obsolete Fields

#### Task 4.1: Remove OpenWeatherMap Fields from HTML

**Prerequisites:** None (can run parallel to Phase 1-3)  
**Estimated Effort:** Small  
**Files:** `static/templates/index.html`

**Context:**
The Settings tab currently contains fields for OpenWeatherMap that are no longer used:
- API Key input field
- Country Code dropdown

These need to be removed and the UI reorganized.

**Current Weather Settings Section:**
- City input
- State/Province input
- Country Code dropdown (remove)
- Temperature Units dropdown (keep)
- OpenWeatherMap API Key input (remove)

**Target Weather Settings Section:**
- Location display (shows current location name)
- "Set Location" button (opens map modal)
- ZIP Code / City search input
- Temperature Units dropdown
- "Test Weather" button

**Changes:**
1. Remove Country Code dropdown and label
2. Remove API Key input and label
3. Add location display area showing current coordinates/name
4. Add "Set Location" button
5. Add search input for ZIP/city lookup
6. Reorganize section layout

**Acceptance Criteria:**
- [ ] API Key field removed
- [ ] Country Code field removed
- [ ] Location display area added
- [ ] "Set Location" button added
- [ ] Search input added

---

#### Task 4.2: Update JavaScript Validation and Save Logic

**Prerequisites:** Task 4.1  
**Estimated Effort:** Medium  
**Files:** `static/js/app.js`

**Context:**
The JavaScript currently validates that API key is present and sends obsolete fields. This needs updating.

**Current `saveSettings()` sends:**
```javascript
weather: {
  city: city,
  state: state,
  country: country,
  units: units,
  api_key: apiKey
}
```

**Target `saveSettings()` sends:**
```javascript
weather: {
  latitude: lat,
  longitude: lon,
  location_name: locationName,
  city: city,
  state: state,
  units: units
}
```

**Changes:**
1. Remove API key validation from `testWeather()`
2. Remove API key from save payload
3. Remove country from save payload
4. Add latitude, longitude, location_name to save payload
5. Update `loadSettings()` to populate new fields
6. Remove references to `weather-api-key` and `weather-country` elements

**Acceptance Criteria:**
- [ ] API key validation removed
- [ ] Save payload includes coordinates
- [ ] Load settings populates location display
- [ ] No references to removed HTML elements

---

### Phase 5: Frontend - Add Map Location Picker

#### Task 5.1: Add Leaflet Dependencies

**Prerequisites:** Task 4.1  
**Estimated Effort:** Small  
**Files:** `static/templates/index.html`

**Context:**
Leaflet is a lightweight JavaScript library for interactive maps. We'll use it with OpenStreetMap tiles (free, no API key required).

**Add to HTML head:**
```html
<!-- Leaflet CSS -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<!-- Leaflet JS -->
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
```

**Implementation Notes:**
- Use CDN for simplicity (no build process needed)
- Leaflet is MIT licensed
- OpenStreetMap tiles are free with attribution

**Acceptance Criteria:**
- [ ] Leaflet CSS included
- [ ] Leaflet JS included
- [ ] No console errors on page load

---

#### Task 5.2: Create Map Modal HTML Structure

**Prerequisites:** Task 5.1  
**Estimated Effort:** Medium  
**Files:** `static/templates/index.html`

**Context:**
The map modal allows users to visually select their location by placing a pin on a map. Inspired by eazyweather's `LocationPinModal`.

**Modal Structure:**
```html
<div id="location-modal" class="modal">
  <div class="modal-content">
    <div class="modal-header">
      <h3>Set Your Location</h3>
      <button class="close-btn">&times;</button>
    </div>
    <div class="modal-body">
      <div id="location-map" style="height: 400px;"></div>
      <div class="location-info">
        <p>Drag the pin or click the map to set your location</p>
        <p id="selected-location">No location selected</p>
        <p id="selected-coords"></p>
      </div>
    </div>
    <div class="modal-footer">
      <button id="use-my-location-btn">📍 Use My Location</button>
      <button id="confirm-location-btn" class="primary">Confirm Location</button>
      <button id="cancel-location-btn">Cancel</button>
    </div>
  </div>
</div>
```

**Features:**
- Map container for Leaflet
- Location name display (updated via reverse geocoding)
- Coordinates display
- "Use My Location" button (browser geolocation)
- Confirm/Cancel buttons

**Acceptance Criteria:**
- [ ] Modal HTML structure added
- [ ] Map container element present
- [ ] Location info display area
- [ ] All buttons present

---

#### Task 5.3: Add Map Modal Styles

**Prerequisites:** Task 5.2  
**Estimated Effort:** Small  
**Files:** `static/css/styles.css`

**Context:**
Style the modal to match existing InkFrame UI and ensure proper map display.

**Styles Needed:**
- Modal overlay (semi-transparent background)
- Modal content (centered, rounded corners)
- Map container (proper height, border)
- Location info styling
- Button styling (match existing)
- Responsive adjustments

**Implementation Notes:**
- Match existing color scheme in styles.css
- Ensure map is visible and interactive
- Modal should be centered vertically and horizontally
- Close button in top-right corner

**Acceptance Criteria:**
- [ ] Modal displays centered on screen
- [ ] Map is properly sized and visible
- [ ] Buttons match existing style
- [ ] Modal closes properly

---

#### Task 5.4: Implement Map Modal JavaScript

**Prerequisites:** Task 5.2, Task 5.3, Task 2.3  
**Estimated Effort:** Large  
**Files:** `static/js/app.js`

**Context:**
This is the core map picker functionality. Based on eazyweather's implementation.

**Functions to Implement:**

1. **`initLocationModal()`**
   - Initialize Leaflet map
   - Set default view (US center or current location)
   - Add OpenStreetMap tile layer
   - Add draggable marker

2. **`openLocationModal()`**
   - Show modal
   - Center map on current saved location (if any)
   - Or center on IP-geolocated position

3. **`closeLocationModal()`**
   - Hide modal
   - Reset any unsaved changes

4. **`onMapClick(e)`**
   - Move marker to clicked position
   - Trigger reverse geocoding
   - Update location display

5. **`onMarkerDrag(e)`**
   - Get new marker position
   - Trigger reverse geocoding
   - Update location display

6. **`reverseGeocode(lat, lon)`**
   - Call `/api/location/reverse`
   - Update `#selected-location` with result
   - Update `#selected-coords` with coordinates

7. **`useMyLocation()`**
   - Request browser geolocation
   - Move map and marker to position
   - Trigger reverse geocoding

8. **`confirmLocation()`**
   - Save selected coordinates to form fields
   - Close modal
   - Update main location display

**Event Listeners:**
- "Set Location" button → `openLocationModal()`
- Map click → `onMapClick()`
- Marker drag end → `onMarkerDrag()`
- "Use My Location" button → `useMyLocation()`
- "Confirm Location" button → `confirmLocation()`
- Close/Cancel buttons → `closeLocationModal()`

**Acceptance Criteria:**
- [ ] Map initializes with OpenStreetMap tiles
- [ ] Marker is draggable
- [ ] Click on map moves marker
- [ ] Reverse geocoding updates location name
- [ ] Browser geolocation works
- [ ] Confirm saves coordinates
- [ ] Cancel discards changes

---

#### Task 5.5: Implement ZIP Code / City Search

**Prerequisites:** Task 2.2, Task 5.4  
**Estimated Effort:** Medium  
**Files:** `static/js/app.js`

**Context:**
Alternative to map picking - user can type a ZIP code or city name and get geocoded results.

**Functions to Implement:**

1. **`searchLocation(query)`**
   - Call `/api/location/geocode` with query
   - Display results (may be multiple)
   - Allow user to select from results

2. **`displaySearchResults(results)`**
   - Show dropdown/list of matching locations
   - Each result shows name and can be clicked
   - Clicking result sets coordinates and updates map

3. **`selectSearchResult(result)`**
   - Set coordinates from result
   - Update location display
   - Move map marker to location
   - Close search results dropdown

**UI Elements:**
- Search input field
- Search button or enter-to-search
- Results dropdown (appears below input)

**Implementation Notes:**
- Debounce search input (300ms) to avoid excessive API calls
- Show loading indicator during search
- Handle "no results found" gracefully
- ZIP code format: 5 digits (US)

**Acceptance Criteria:**
- [ ] Search input accepts ZIP code and city names
- [ ] Results display as selectable list
- [ ] Selecting result updates coordinates
- [ ] Map marker moves to selected location
- [ ] Error handling for no results

---

### Phase 6: Testing and Documentation

#### Task 6.1: Update Test Weather Button

**Prerequisites:** Task 4.2, Task 3.1  
**Estimated Effort:** Small  
**Files:** `static/js/app.js`

**Context:**
The "Test Weather" button should verify the weather.gov API works with the configured location.

**Current Behavior:**
- Validates API key is present (obsolete)
- Calls `/api/weather/status`
- Displays result

**Target Behavior:**
- Validates coordinates are set (or fallback will be used)
- Calls `/api/weather/refresh` to force fresh data
- Displays current weather and location source
- Shows clear success/failure message

**Changes:**
1. Remove API key validation
2. Update success message to show location used
3. Add location source indicator (coordinates, IP geolocation, default)

**Acceptance Criteria:**
- [ ] Test works without API key
- [ ] Shows location being used
- [ ] Clear success/failure indication
- [ ] Displays actual weather data

---

#### Task 6.2: Add Migration Notice

**Prerequisites:** Task 3.1  
**Estimated Effort:** Small  
**Files:** `static/js/app.js`, `static/templates/index.html`

**Context:**
Users upgrading from v1.1.x may have city/state configured but no coordinates. Show a one-time notice encouraging them to set their precise location.

**Implementation:**
1. On settings load, check if coordinates are missing but city/state exist
2. Show info banner: "📍 We've updated location settings! Click 'Set Location' to pin your exact position for better weather accuracy."
3. Banner dismissible (save dismiss state to localStorage)

**Acceptance Criteria:**
- [ ] Migration notice appears for legacy configs
- [ ] Notice is dismissible
- [ ] Notice doesn't appear after dismissal
- [ ] Notice doesn't appear for new/complete configs

---

#### Task 6.3: Update Version and Documentation

**Prerequisites:** All previous tasks  
**Estimated Effort:** Small  
**Files:** `src/version.py`, `AGENTS.md`, `docs/changelog.md`

**Context:**
This is a MINOR version bump as it adds new features (map picker, ZIP search) without breaking existing functionality.

**Changes to `src/version.py`:**
```python
__version__ = "1.2.0"
VERSION_STRING = "1.2.0"
VERSION_FULL = "InkFrame v1.2.0"
```

**Changes to `AGENTS.md`:**
Add to Version History section:
```markdown
### v1.2.0 - 2026-01-XX
- **NEW**: Interactive map-based location picker with Leaflet
- **NEW**: ZIP code and city name search for location
- **NEW**: Geocoding API endpoints (/api/location/geocode, /api/location/reverse)
- **REMOVED**: OpenWeatherMap API key field (obsolete)
- **REMOVED**: Country code field (weather.gov is US-only)
- **IMPROVED**: Weather client prioritizes stored coordinates
- **IMPROVED**: Auto-migration of legacy city/state configs
- **UI**: Streamlined weather settings interface
```

**Changes to `docs/changelog.md`:**
Add detailed changelog entry with all changes.

**Acceptance Criteria:**
- [ ] Version bumped to 1.2.0
- [ ] AGENTS.md version history updated
- [ ] changelog.md updated
- [ ] Current version section in AGENTS.md updated

---

## Task Dependency Graph

```
Phase 1: Config Schema
├── Task 1.1: Update default_config.json
└── Task 1.2: Update config_manager.py (depends on 1.1)

Phase 2: Backend API (depends on Phase 1)
├── Task 2.1: Update Flask config endpoint
├── Task 2.2: Add geocoding endpoint
└── Task 2.3: Add reverse geocoding endpoint (depends on 2.2)

Phase 3: Weather Client (depends on Phase 1)
└── Task 3.1: Update weather client

Phase 4: Frontend Cleanup (parallel with Phase 1-3)
├── Task 4.1: Remove obsolete HTML fields
└── Task 4.2: Update JavaScript (depends on 4.1)

Phase 5: Map Picker (depends on Phase 2, 4)
├── Task 5.1: Add Leaflet dependencies
├── Task 5.2: Create modal HTML (depends on 5.1)
├── Task 5.3: Add modal styles (depends on 5.2)
├── Task 5.4: Implement map JavaScript (depends on 5.2, 5.3, 2.3)
└── Task 5.5: Implement search (depends on 2.2, 5.4)

Phase 6: Testing & Docs (depends on all)
├── Task 6.1: Update test weather button
├── Task 6.2: Add migration notice
└── Task 6.3: Update version and docs
```

## Execution Order (Recommended)

1. **Task 1.1** - Update default_config.json
2. **Task 1.2** - Update config_manager.py
3. **Task 4.1** - Remove obsolete HTML fields (parallel)
4. **Task 2.1** - Update Flask config endpoint
5. **Task 2.2** - Add geocoding endpoint
6. **Task 2.3** - Add reverse geocoding endpoint
7. **Task 3.1** - Update weather client
8. **Task 4.2** - Update JavaScript
9. **Task 5.1** - Add Leaflet dependencies
10. **Task 5.2** - Create modal HTML
11. **Task 5.3** - Add modal styles
12. **Task 5.4** - Implement map JavaScript
13. **Task 5.5** - Implement search
14. **Task 6.1** - Update test weather button
15. **Task 6.2** - Add migration notice
16. **Task 6.3** - Update version and docs

---

## Testing Checklist

### Manual Testing

- [ ] Fresh install works with no prior config
- [ ] Existing city/state config triggers migration notice
- [ ] Map modal opens and displays correctly
- [ ] Pin is draggable on map
- [ ] Click on map moves pin
- [ ] "Use My Location" gets browser GPS
- [ ] Reverse geocoding shows location name
- [ ] ZIP code search returns results
- [ ] City name search returns results
- [ ] Selecting search result updates map
- [ ] Confirm location saves coordinates
- [ ] Test Weather button works with coordinates
- [ ] Test Weather button works with IP fallback
- [ ] Temperature units setting works
- [ ] Timezone setting works
- [ ] Settings persist after page reload
- [ ] E-ink display shows weather with new config

### API Testing

- [ ] GET /api/config returns new schema (no api_key)
- [ ] POST /api/config accepts coordinates
- [ ] POST /api/location/geocode works with ZIP
- [ ] POST /api/location/geocode works with city
- [ ] POST /api/location/reverse returns location name
- [ ] Rate limiting prevents Nominatim abuse

---

## Rollback Plan

If issues arise, the changes can be rolled back by:
1. Reverting to v1.1.1 tag
2. Config files remain compatible (new fields ignored by old code)
3. City/state fields preserved for backwards compatibility

---

## Security Considerations

- No API keys stored or transmitted (security improvement)
- Nominatim requests include User-Agent for identification
- Browser geolocation requires user permission
- No sensitive data exposed in API responses

---

## Notes for AI Agents

When implementing these tasks:

1. **Follow AGENTS.md guidelines** for code organization and commit messages
2. **Test in simulation mode** before hardware deployment
3. **Use conventional commits** (feat:, fix:, docs:, etc.)
4. **Update AGENTS.md** when adding new API endpoints
5. **Check for errors** after each file modification
6. **Preserve existing functionality** - this is additive, not a rewrite
7. **Reference eazyweather** for Leaflet implementation patterns if needed

### Key References

- EazyWeather LocationPinModal: https://github.com/spenceriam/eazyweather
- Nominatim API docs: https://nominatim.org/release-docs/latest/api/Search/
- Leaflet docs: https://leafletjs.com/reference.html
- weather.gov API: https://www.weather.gov/documentation/services-web-api
