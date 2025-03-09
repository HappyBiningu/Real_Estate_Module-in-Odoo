# Real Estate Management Module for Odoo

A comprehensive Odoo module for managing and advertising real estate properties with listing, search, and status management capabilities.

## Features

- **Property Management**
  - Detailed property information (price, size, rooms, amenities, etc.)
  - Property image galleries
  - Property status tracking (new, offer received, offer accepted, sold, canceled, rented)
  - Assign properties to salespeople

- **Property Types and Tags**
  - Categorize properties by type (apartment, house, commercial, etc.)
  - Tag properties with specific features (renovated, sea view, etc.)

- **Offer Management**
  - Track and manage offers for properties
  - Accept or refuse offers
  - Set offer validity periods
  - Automatic property status updates based on offers

- **User-friendly Interface**
  - Kanban view for visual property management
  - Detailed form views
  - Advanced search filters
  - Analytics and reporting tools

## Installation

1. Download the module and place it in your Odoo addons directory.
2. Update the module list in Odoo:
   - Navigate to `Apps > Update Apps List`
3. Install the module:
   - Navigate to `Apps > Apps`
   - Search for "Real Estate Management"
   - Click "Install"

## Configuration

After installation, you can configure the module:

1. Create property types:
   - Navigate to `Real Estate > Configuration > Property Types`
   - Create types like "Apartment", "House", "Commercial", etc.

2. Create property tags:
   - Navigate to `Real Estate > Configuration > Property Tags`
   - Create tags like "Renovated", "Sea View", "City Center", etc.

3. Set up access rights:
   - Navigate to `Settings > Users & Companies > Users`
   - Assign users to the "Real Estate / User" or "Real Estate / Manager" groups

## Usage

### Creating Properties

1. Navigate to `Real Estate > Properties`
2. Click "Create" to add a new property
3. Fill in the property details:
   - Title and description
   - Property type
   - Expected price
   - Available date
   - Address details
   - Features (bedrooms, living area, etc.)
   - Add property images

### Managing Offers

1. Navigate to a property form
2. In the "Offers" tab, add a new offer with:
   - Partner (potential buyer)
   - Price
   - Validity period
3. Accept or refuse offers using the corresponding buttons
4. When an offer is accepted, the property status changes to "Offer Accepted"

### Selling Properties

1. Navigate to a property with an accepted offer
2. Click the "Sold" button to mark the property as sold
3. The buyer and selling price are automatically recorded from the accepted offer

### Reporting

1. Navigate to `Real Estate > Properties`
2. Use the Graph or Pivot view to analyze your property portfolio
3. Filter and group data by various criteria (property type, status, salesperson, etc.)

## Technical Information

- **Dependencies**: `base`, `mail`, `web`
- **Models**:
  - `real.estate.property`
  - `real.estate.property.type`
  - `real.estate.property.tag`
  - `real.estate.property.offer`
  - `real.estate.property.image`
- **Views**: Form, Tree, Kanban, Search, Calendar, Pivot, Graph
- **Security**: User and Manager access levels

## Development

The module follows Odoo's development guidelines and best practices:

- Models structured according to Odoo standards
- Proper view inheritance
- Security rules for access control
- Module dependencies properly defined
- Responsive design for property listings

## Support

For any questions or support needs, please contact:

- Email: happybiningu@icloud.com
- Website: https://tinobiningu.netlify.app
