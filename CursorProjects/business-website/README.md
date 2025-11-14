# Business Website

A modern, responsive website for small businesses featuring company information, product displays, and appointment booking functionality.

## Features

- **Home Page**: Welcome section with company overview and key features
- **About Page**: Company story, mission, values, and team information
- **Products Page**: Display your products/services with descriptions
- **Appointment Booking**: Customer appointment request form
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Modern UI**: Clean, professional design with smooth animations

## Getting Started

1. **Open the Website**: Simply open `index.html` in your web browser, or use a local web server for best results.

2. **Using a Local Server** (Recommended):
   - **Python**: Run `python -m http.server 8000` in the project directory, then visit `http://localhost:8000`
   - **Node.js**: Install `http-server` with `npm install -g http-server`, then run `http-server` in the project directory
   - **VS Code**: Use the "Live Server" extension

## Customization Guide

### 1. Update Business Information

**Replace "Your Business Name" throughout all files:**
- Search and replace in all HTML files
- Update the navigation brand name
- Update footer copyright

**Update Contact Information** (in all HTML files):
- Email: `info@yourbusiness.com`
- Phone: `(555) 123-4567`
- Address: `123 Main St, City, State 12345`
- Business Hours

### 2. Customize Colors

Edit `styles.css` and modify the CSS variables at the top:
```css
:root {
    --primary-color: #2563eb;      /* Main brand color */
    --primary-dark: #1e40af;       /* Darker shade for hover states */
    --secondary-color: #64748b;    /* Secondary text color */
    /* ... other colors ... */
}
```

### 3. Update Products

Edit `products.html`:
- Replace the product cards with your actual products
- Update product names, descriptions, and images
- Replace emoji placeholders (📦) with actual product images if desired

### 4. Customize About Page

Edit `about.html`:
- Update the company story section
- Modify mission and values
- Add your team members' information
- Replace `[YEAR]` with your founding year

### 5. Configure Appointment Booking

The appointment form currently shows a success message after submission. To actually receive appointments:

**Option 1: Email Integration**
- Use a service like Formspree, EmailJS, or similar
- Update the `sendToBackend()` function in `script.js`

**Option 2: Backend API**
- Create a backend endpoint to handle form submissions
- Uncomment and modify the `sendToBackend()` function in `script.js`
- Update the API endpoint URL

**Option 3: Manual Processing**
- The form data is logged to the browser console
- You can check the console to see submitted appointments
- Consider adding a simple email notification service

### 6. Add Product Images

Replace the emoji placeholders (📦) with actual images:
1. Create an `images` folder in the project directory
2. Add your product images
3. Update the HTML: `<div class="product-image">📦</div>` to `<img src="images/product1.jpg" alt="Product Name" class="product-image">`
4. Update CSS if needed for image styling

## File Structure

```
business-website/
├── index.html          # Home page
├── about.html          # About page
├── products.html       # Products page
├── appointments.html   # Appointment booking page
├── styles.css          # All styling
├── script.js           # JavaScript functionality
└── README.md           # This file
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Next Steps

1. **Customize Content**: Replace all placeholder text with your actual business information
2. **Add Images**: Replace emoji placeholders with real product/service images
3. **Set Up Appointment Handling**: Configure email or backend integration for appointment submissions
4. **Deploy**: Host your website using services like:
   - GitHub Pages (free)
   - Netlify (free)
   - Vercel (free)
   - Traditional web hosting

## Notes

- This website does NOT handle payments or orders (as requested)
- All appointment submissions are currently handled client-side
- You'll need to set up backend/email integration to actually receive appointment requests
- The design is fully responsive and works on all device sizes

## Support

For questions or issues, please refer to the code comments or customize as needed for your specific business requirements.

