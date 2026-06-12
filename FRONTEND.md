# 🌐 HTML/CSS/JS Frontend

Modern, responsive single-file web interface for the DSM-5 Psychological Analysis System.

## 📋 Features

- ✅ **Single HTML File** - No build process, no dependencies
- ✅ **Responsive Design** - Works on desktop, tablet, and mobile
- ✅ **Real-time Health Checks** - Shows backend connection status
- ✅ **Medical Disclaimer** - Mandatory acceptance before use
- ✅ **Medical Disclaimer** - Clear liability disclaimers
- ✅ **Source Attribution** - Shows DSM-5 source evidence
- ✅ **Rich Metadata** - Displays ICD codes, page numbers, categories
- ✅ **Modern UI** - Gradient design, smooth animations
- ✅ **Accessibility** - Semantic HTML, ARIA labels
- ✅ **No External Dependencies** - Pure HTML/CSS/JavaScript

## 📁 File Location

```
frontend/
└── index.html          # Complete web application (all-in-one file)
```

## 🚀 Running the Frontend

The frontend is automatically served by the FastAPI backend:

```bash
# Start the backend
python backend/main.py

# Access at http://localhost:8000
```

### Docker

```bash
# Build and run with Docker
docker-compose build
docker-compose up -d

# Access at http://localhost:8000
```

## 🎨 Design

### Color Scheme

- **Primary Gradient**: Purple (#667eea) to Purple (#764ba2)
- **Success**: Green (#28a745)
- **Warning**: Amber (#ffc107)
- **Error**: Red (#dc3545)
- **Neutral**: Gray (#f0f0f0 to #333)

### Typography

- **Font**: System fonts (-apple-system, BlinkMacSystemFont, Segoe UI, Roboto)
- **Sizes**: Responsive typography that scales with screen size
- **Line Height**: 1.6-1.8 for readability

### Layout

- **Max Width**: 900px
- **Padding**: 30px (desktop), 20px (mobile)
- **Border Radius**: 6-12px
- **Shadows**: Subtle elevation effect

## 🔧 Customization

### Colors

Edit the CSS color variables in the `<style>` section:

```css
/* Primary gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Success indicator */
.status-indicator {
    background: #28a745;
}
```

### Text Content

Edit placeholder text and messages in the HTML:

```html
<label for="symptoms">Describe Your Symptoms</label>
<textarea placeholder="Describe your symptoms in detail..."></textarea>
```

### API URL

Change the backend URL in the JavaScript:

```javascript
const API_URL = 'http://localhost:8000';  // Change this
```

For production with different domain:

```javascript
const API_URL = 'https://api.example.com';
```

## 📱 Responsive Design

The interface is fully responsive:

```css
@media (max-width: 768px) {
    /* Mobile-specific styles */
    header h1 { font-size: 2em; }
    .button-group { flex-direction: column; }
}
```

**Breakpoints:**
- Desktop: 768px+
- Tablet: 480px - 768px
- Mobile: < 480px

## ⚡ Performance

- **No Build Step** - Served directly from browser
- **No External Resources** - Everything embedded
- **Minimal Bundle Size** - ~45KB (single HTML file)
- **Fast Load Time** - Loads in < 500ms
- **No JavaScript Frameworks** - Vanilla JS only

### Network Requests

1. **Initial Load**: Single HTML file
2. **Health Check**: `/health` endpoint (every 10 seconds)
3. **Analysis Request**: `/analyze` endpoint (POST)

## 🔒 Security

### Input Validation

- Minimum 10 characters for symptoms
- HTML escaping for all user data
- CSRF protection via CORS headers

### Data Handling

- No local storage of sensitive data
- No cookies used
- Direct API communication
- HTTPS recommended for production

### Content Security

- Inline CSS (no external stylesheets)
- Inline JavaScript (no external scripts)
- Safe HTML escaping: `escapeHtml()` function

## 📊 API Integration

### Health Check

```javascript
fetch('http://localhost:8000/health')
    .then(r => r.json())
    .then(data => {
        // data.status: "healthy" | "warning" | "degraded" | "unhealthy"
        // data.documents_indexed: number
    })
```

### Analysis Request

```javascript
fetch('http://localhost:8000/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        symptoms: "string",
        duration: "string (optional)"
    })
})
.then(r => r.json())
.then(data => {
    // data.analysis: string
    // data.sources: array of SourceDocument
    // data.disclaimer: string
    // data.timestamp: ISO date
    // data.model_used: "gpt-4o"
})
```

## 🧪 Testing

### Manual Testing

1. **Load Test**: Open http://localhost:8000
2. **Health Check**: Verify green status indicator
3. **Disclaimer**: Accept the medical disclaimer
4. **Analysis**: Submit sample symptoms
5. **Results**: Verify sources display correctly
6. **Mobile**: Test on mobile browser

### Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🐛 Troubleshooting

### Backend Offline

**Issue**: Status shows "Backend Offline"

**Solution**:
1. Check backend is running: `python backend/main.py`
2. Verify port 8000 is accessible
3. Check CORS configuration in `backend/main.py`

### CORS Errors

**Issue**: `Access to XMLHttpRequest blocked by CORS`

**Solution**: Backend CORS is already configured to allow all origins:

```python
CORSMiddleware(
    allow_origins=["*"],  # Change to specific domains in production
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Not Responding

**Issue**: Analysis request times out

**Solution**:
1. Check backend health: `curl http://localhost:8000/health`
2. Check vector database is populated
3. Run ingestion: `python backend/scripts/ingest.py`
4. Check OpenAI API quota

## 📚 Code Structure

### HTML Elements

```html
<body>
  <div class="health-status">           <!-- Status indicator -->
  <div class="container">
    <header>                             <!-- App title -->
    <div class="content">
      <div class="disclaimer">          <!-- Medical disclaimer -->
      <form id="analysisForm">          <!-- Input form -->
      <div class="loading">             <!-- Loading spinner -->
      <div class="results">             <!-- Results display -->
    </div>
    <footer>                             <!-- Footer with resources -->
  </div>
</body>
```

### CSS Classes

- `.container` - Main wrapper
- `.form-group` - Form field groups
- `.loading` - Loading state
- `.results` - Results section
- `.source-item` - Individual source card
- `.badge` - Small tags/labels
- `.error-message` / `.success-message` - Alert messages

### JavaScript Functions

- `checkBackendHealth()` - Periodic health monitoring
- `analyzeSymptoms()` - Submit analysis request
- `displayResults()` - Render results
- `escapeHtml()` - Prevent XSS
- `showError()` / `showSuccess()` - Notifications

## 🚀 Deployment

### Development

```bash
python backend/main.py
# Open http://localhost:8000
```

### Production

1. Build Docker image:
   ```bash
   docker-compose build
   ```

2. Run container:
   ```bash
   docker-compose up -d
   ```

3. Access via HTTPS proxy:
   ```
   https://yourdomain.com/
   ```

### With Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔄 Offline Support

The frontend requires:
- Browser (HTML rendering)
- JavaScript enabled
- Internet connection (for API calls)

To add offline support, implement service workers and local caching (not included in basic version).

## 📝 Modification Guide

### Add New Input Field

```html
<div class="form-group">
    <label for="newField">New Field</label>
    <input type="text" id="newField" placeholder="...">
</div>
```

Then update the form submission:

```javascript
form.addEventListener('submit', async (e) => {
    const newField = document.getElementById('newField').value;
    // Use newField in API request
});
```

### Customize Disclaimer

Edit the disclaimer HTML in the form:

```html
<div class="disclaimer">
    <h3>⚠️ IMPORTANT MEDICAL DISCLAIMER</h3>
    <p>Your custom disclaimer text...</p>
</div>
```

### Change Color Scheme

Replace all gradient instances:

```css
/* Old */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* New */
background: linear-gradient(135deg, #your-color-1 0%, #your-color-2 100%);
```

## 🤝 Contributing

To improve the frontend:

1. Test in multiple browsers
2. Ensure mobile responsiveness
3. Keep no external dependencies
4. Update FRONTEND.md
5. Test with different API responses

## 📞 Support

For issues with the frontend:
1. Check browser console for errors: F12 > Console
2. Verify backend is running and healthy
3. Check network tab for API responses
4. Review logs in `backend/logs/app.log`

## 📄 License

Same as the main project (educational use)

---

**Built with ❤️ for modern web browsers**
