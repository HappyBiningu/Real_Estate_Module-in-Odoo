#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Real Estate Module Demonstration Script
=======================================

This script demonstrates the structure and features of the Real Estate module without requiring
a running Odoo server. It shows the data models, relationships, and business logic.
"""

import os
import sys
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any, Optional, Union

# ----------------------------------------------------------------------------------
# Mock Odoo Environment
# ----------------------------------------------------------------------------------

class Model:
    """Base class to mimic Odoo's model system"""
    _name = None
    _description = None
    _order = None
    
    def __init__(self, values=None):
        self.id = id(self)
        self._values = values or {}
        for key, value in self._values.items():
            setattr(self, key, value)
    
    def write(self, values):
        """Update record values"""
        for key, value in values.items():
            setattr(self, key, value)
            self._values[key] = value
        return True
    
    def get_values(self):
        """Get all values as a dictionary"""
        return {k: getattr(self, k, None) for k in self._values.keys()}

    def __str__(self):
        return f"{self._name}({self.id})"

    def __repr__(self):
        return self.__str__()


# ----------------------------------------------------------------------------------
# Real Estate Models
# ----------------------------------------------------------------------------------

class PropertyType(Model):
    """Property Type model"""
    _name = 'real.estate.property.type'
    _description = 'Real Estate Property Type'
    _order = 'sequence, name'
    
    def __init__(self, values=None):
        values = values or {}
        default_values = {
            'name': '',
            'sequence': 10,
            'property_ids': [],
            'property_count': 0,
            'description': '',
            'color': 0,
        }
        default_values.update(values)
        super().__init__(default_values)


class PropertyTag(Model):
    """Property Tag model"""
    _name = 'real.estate.property.tag'
    _description = 'Real Estate Property Tag'
    _order = 'name'
    
    def __init__(self, values=None):
        values = values or {}
        default_values = {
            'name': '',
            'color': 0,
        }
        default_values.update(values)
        super().__init__(default_values)


class PropertyImage(Model):
    """Property Image model"""
    _name = 'real.estate.property.image'
    _description = 'Property Image'
    _order = 'sequence, id'
    
    def __init__(self, values=None):
        values = values or {}
        default_values = {
            'name': '',
            'sequence': 10,
            'image': None,  # This would be binary data in real Odoo
            'property_id': None,
            'description': '',
        }
        default_values.update(values)
        super().__init__(default_values)


class PropertyOffer(Model):
    """Property Offer model"""
    _name = 'real.estate.property.offer'
    _description = 'Real Estate Property Offer'
    _order = 'price desc'
    
    def __init__(self, values=None, property_obj=None):
        values = values or {}
        default_values = {
            'price': 0.0,
            'status': 'pending',  # pending, accepted, refused
            'partner_id': None,  # Would be res.partner in real Odoo
            'property_id': property_obj.id if property_obj else None,
            'validity': 7,
            'date_deadline': (datetime.now() + timedelta(days=7)).date(),
            'create_date': datetime.now(),
        }
        default_values.update(values)
        super().__init__(default_values)
        self._property = property_obj
    
    def action_accept(self):
        """Accept this offer"""
        if not self._property:
            print("Error: Property not found for this offer")
            return False
        
        # Update offer status
        self.write({'status': 'accepted'})
        
        # Update property state and selling info
        self._property.write({
            'state': 'offer_accepted',
            'selling_price': self.price,
            'buyer_id': self.partner_id,
        })
        
        print(f"✅ Offer accepted: ${self.price} from {self.partner_id}")
        return True
    
    def action_refuse(self):
        """Refuse this offer"""
        self.write({'status': 'refused'})
        print(f"❌ Offer refused: ${self.price} from {self.partner_id}")
        return True


class Property(Model):
    """Property model"""
    _name = 'real.estate.property'
    _description = 'Real Estate Property'
    _order = 'id desc'
    
    def __init__(self, values=None):
        values = values or {}
        default_values = {
            'name': '',
            'description': '',
            'postcode': '',
            'date_availability': (datetime.now() + timedelta(days=90)).date(),
            'expected_price': 0.0,
            'selling_price': 0.0,
            'bedrooms': 2,
            'living_area': 0,
            'facades': 0,
            'garage': False,
            'garden': False,
            'garden_area': 0,
            'garden_orientation': False,  # north, south, east, west
            'state': 'new',  # new, offer_received, offer_accepted, sold, canceled
            'active': True,
            'property_type_id': None,
            'user_id': None,  # Would be res.users in real Odoo
            'buyer_id': None,  # Would be res.partner in real Odoo
            'tag_ids': [],  # Would be m2m in real Odoo
            'offer_ids': [],  # Would be o2m in real Odoo
            'total_area': 0,
            'best_offer': 0.0,
            'address': '',
            'city': '',
            'country_id': None,
            'property_image_ids': [],
            'main_image_id': None,
            'amenities': '',
            'furnished': False,
        }
        default_values.update(values)
        super().__init__(default_values)
        self._offers = []
        
        # Handle garden defaults
        if self.garden and self.garden_area == 0:
            self.garden_area = 10
            self.garden_orientation = 'north'
            
        # Calculate derived fields
        self._compute_total_area()
    
    def _compute_total_area(self):
        """Compute the total area"""
        self.total_area = self.living_area + self.garden_area
    
    def _compute_best_offer(self):
        """Compute best offer"""
        if self._offers:
            self.best_offer = max(offer.price for offer in self._offers)
        else:
            self.best_offer = 0.0
    
    def create_offer(self, price, partner_id):
        """Create a new offer for this property"""
        if self.state in ['sold', 'canceled']:
            print(f"Error: Cannot create offer for property in '{self.state}' state")
            return None
            
        # Check if price is higher than existing offers
        if self._offers:
            max_offer = max(offer.price for offer in self._offers)
            if price <= max_offer:
                print(f"Error: Offer must be higher than ${max_offer}")
                return None
        
        # Create the offer
        offer = PropertyOffer({
            'price': price,
            'partner_id': partner_id,
            'property_id': self.id,
        }, property_obj=self)
        
        self._offers.append(offer)
        self.offer_ids.append(offer.id)
        
        # Update state if this is the first offer
        if self.state == 'new':
            self.state = 'offer_received'
            
        # Update best offer
        self._compute_best_offer()
        
        print(f"🏠 New offer created: ${price} for property '{self.name}'")
        return offer
    
    def action_sold(self):
        """Mark the property as sold"""
        if self.state == 'canceled':
            print("Error: Canceled properties cannot be sold")
            return False
        if not self.buyer_id:
            print("Error: Cannot sell a property without a buyer")
            return False
            
        self.state = 'sold'
        print(f"🎉 Property sold: '{self.name}' for ${self.selling_price}")
        return True
    
    def action_cancel(self):
        """Cancel the property"""
        if self.state == 'sold':
            print("Error: Sold properties cannot be canceled")
            return False
            
        self.state = 'canceled'
        print(f"🚫 Property canceled: '{self.name}'")
        return True
    
    def add_tag(self, tag):
        """Add a tag to the property"""
        if tag.id not in self.tag_ids:
            self.tag_ids.append(tag.id)
            print(f"🏷️ Tag added: '{tag.name}' to property '{self.name}'")
        return True
    
    def set_property_type(self, property_type):
        """Set the property type"""
        self.property_type_id = property_type.id
        print(f"🏢 Property type set: '{property_type.name}' for property '{self.name}'")
        return True


# ----------------------------------------------------------------------------------
# Demo Functions
# ----------------------------------------------------------------------------------

def create_demo_data():
    """Create demo data for the real estate module"""
    # Create property types
    apartment = PropertyType({'name': 'Apartment', 'sequence': 10})
    house = PropertyType({'name': 'House', 'sequence': 20})
    commercial = PropertyType({'name': 'Commercial', 'sequence': 30})
    land = PropertyType({'name': 'Land', 'sequence': 40})
    
    # Create property tags
    renovated = PropertyTag({'name': 'Renovated', 'color': 1})
    sea_view = PropertyTag({'name': 'Sea View', 'color': 2})
    garden = PropertyTag({'name': 'Garden', 'color': 3})
    city_center = PropertyTag({'name': 'City Center', 'color': 4})
    luxury = PropertyTag({'name': 'Luxury', 'color': 5})
    
    # Create properties
    p1 = Property({
        'name': 'Modern Apartment in City Center',
        'description': 'A beautiful modern apartment in the heart of the city.',
        'expected_price': 250000,
        'bedrooms': 2,
        'living_area': 85,
        'garage': True,
        'address': '123 Main St',
        'city': 'New York',
        'amenities': 'Air conditioning, Security system, Hardwood floors',
        'user_id': 'John Doe',
    })
    p1.set_property_type(apartment)
    p1.add_tag(renovated)
    p1.add_tag(city_center)
    
    p2 = Property({
        'name': 'Luxury Beach House',
        'description': 'Stunning beach house with amazing ocean views.',
        'expected_price': 750000,
        'bedrooms': 4,
        'living_area': 210,
        'garage': True,
        'garden': True,
        'garden_area': 150,
        'garden_orientation': 'south',
        'address': '456 Ocean Drive',
        'city': 'Miami',
        'amenities': 'Pool, Outdoor kitchen, Private beach access',
        'user_id': 'Jane Smith',
    })
    p2.set_property_type(house)
    p2.add_tag(sea_view)
    p2.add_tag(luxury)
    p2.add_tag(garden)
    
    p3 = Property({
        'name': 'Commercial Office Space',
        'description': 'Prime location commercial office space for business use.',
        'expected_price': 500000,
        'living_area': 150,
        'address': '789 Business Ave',
        'city': 'Chicago',
        'amenities': 'Meeting rooms, Kitchen area, High-speed internet',
        'user_id': 'Robert Johnson',
    })
    p3.set_property_type(commercial)
    p3.add_tag(city_center)
    
    # Create offers
    p1.create_offer(230000, 'Alice Brown')
    p1.create_offer(240000, 'Bob Wilson')
    
    p2.create_offer(700000, 'Charlie Davis')
    offer = p2.create_offer(730000, 'Diana Evans')
    offer.action_accept()
    
    return {
        'property_types': [apartment, house, commercial, land],
        'property_tags': [renovated, sea_view, garden, city_center, luxury],
        'properties': [p1, p2, p3],
    }


def display_property(property_obj):
    """Display property details in a formatted way"""
    print("=" * 60)
    print(f"🏠 {property_obj.name}")
    print("=" * 60)
    
    # Basic information
    print(f"Description: {property_obj.description}")
    print(f"Status: {property_obj.state}")
    print(f"Expected Price: ${property_obj.expected_price}")
    if property_obj.selling_price:
        print(f"Selling Price: ${property_obj.selling_price}")
    
    # Location
    print(f"Location: {property_obj.address}, {property_obj.city}")
    
    # Features
    print(f"Bedrooms: {property_obj.bedrooms}")
    print(f"Living Area: {property_obj.living_area} sqm")
    print(f"Total Area: {property_obj.total_area} sqm")
    if property_obj.garage:
        print("✓ Garage")
    if property_obj.garden:
        print(f"✓ Garden: {property_obj.garden_area} sqm, {property_obj.garden_orientation} orientation")
    if property_obj.furnished:
        print("✓ Furnished")
    
    # Amenities
    if property_obj.amenities:
        print(f"Amenities: {property_obj.amenities}")
    
    # Salesperson
    print(f"Salesperson: {property_obj.user_id}")
    
    # Tags
    if property_obj.tag_ids:
        print("Tags: " + ", ".join([str(tag_id) for tag_id in property_obj.tag_ids]))
    
    # Offers
    if property_obj._offers:
        print("\nOffers:")
        for i, offer in enumerate(property_obj._offers, 1):
            print(f"  {i}. ${offer.price} from {offer.partner_id} - Status: {offer.status}")
            print(f"     Deadline: {offer.date_deadline}")
    
    # Buyer (if sold)
    if property_obj.state in ['offer_accepted', 'sold'] and property_obj.buyer_id:
        print(f"\nBuyer: {property_obj.buyer_id}")
    
    print()


def interactive_demo():
    """Run an interactive demo of the Real Estate module"""
    print("\n" + "=" * 80)
    print(" 🏢 REAL ESTATE MANAGEMENT MODULE DEMO".center(80))
    print("=" * 80 + "\n")
    
    # Create demo data
    print("Initializing demo data...")
    data = create_demo_data()
    
    properties = data['properties']
    property_types = data['property_types']
    property_tags = data['property_tags']
    
    while True:
        print("\nMain Menu:")
        print("1. View all properties")
        print("2. View property details")
        print("3. Create a new property")
        print("4. Create an offer for a property")
        print("5. Manage property offers")
        print("6. View property types")
        print("7. View property tags")
        print("8. Exit")
        
        choice = input("\nSelect an option (1-8): ")
        
        if choice == '1':
            # View all properties
            print("\nAll Properties:")
            for i, prop in enumerate(properties, 1):
                print(f"{i}. {prop.name} - {prop.state} - ${prop.expected_price}")
        
        elif choice == '2':
            # View property details
            if not properties:
                print("No properties available.")
                continue
                
            print("\nSelect a property to view details:")
            for i, prop in enumerate(properties, 1):
                print(f"{i}. {prop.name}")
                
            try:
                idx = int(input("Enter property number: ")) - 1
                if 0 <= idx < len(properties):
                    display_property(properties[idx])
                else:
                    print("Invalid property number.")
            except ValueError:
                print("Please enter a valid number.")
        
        elif choice == '3':
            # Create a new property
            name = input("Property Title: ")
            desc = input("Description: ")
            price = float(input("Expected Price: "))
            bedrooms = int(input("Bedrooms: "))
            area = int(input("Living Area (sqm): "))
            
            print("\nSelect a property type:")
            for i, t in enumerate(property_types, 1):
                print(f"{i}. {t.name}")
            
            try:
                type_idx = int(input("Enter type number: ")) - 1
                if 0 <= type_idx < len(property_types):
                    prop = Property({
                        'name': name,
                        'description': desc,
                        'expected_price': price,
                        'bedrooms': bedrooms,
                        'living_area': area,
                        'user_id': 'Demo User',
                    })
                    prop.set_property_type(property_types[type_idx])
                    properties.append(prop)
                    print(f"Property '{name}' created successfully!")
                else:
                    print("Invalid type number.")
            except ValueError:
                print("Please enter a valid number.")
        
        elif choice == '4':
            # Create an offer for a property
            if not properties:
                print("No properties available.")
                continue
                
            print("\nSelect a property to make an offer:")
            for i, prop in enumerate(properties, 1):
                if prop.state not in ['sold', 'canceled']:
                    print(f"{i}. {prop.name} - Expected: ${prop.expected_price}")
                
            try:
                idx = int(input("Enter property number: ")) - 1
                if 0 <= idx < len(properties):
                    prop = properties[idx]
                    if prop.state in ['sold', 'canceled']:
                        print("This property is not available for offers.")
                        continue
                        
                    price = float(input("Offer amount: $"))
                    partner = input("Buyer name: ")
                    
                    offer = prop.create_offer(price, partner)
                    if offer:
                        print(f"Offer created successfully!")
                else:
                    print("Invalid property number.")
            except ValueError:
                print("Please enter a valid number.")
        
        elif choice == '5':
            # Manage property offers
            if not properties:
                print("No properties available.")
                continue
                
            print("\nSelect a property to manage offers:")
            for i, prop in enumerate(properties, 1):
                if prop._offers:
                    print(f"{i}. {prop.name} - {len(prop._offers)} offer(s)")
                
            try:
                idx = int(input("Enter property number: ")) - 1
                if 0 <= idx < len(properties):
                    prop = properties[idx]
                    if not prop._offers:
                        print("This property has no offers.")
                        continue
                        
                    print(f"\nOffers for '{prop.name}':")
                    for i, offer in enumerate(prop._offers, 1):
                        print(f"{i}. ${offer.price} from {offer.partner_id} - Status: {offer.status}")
                    
                    offer_idx = int(input("Select offer number to manage: ")) - 1
                    if 0 <= offer_idx < len(prop._offers):
                        offer = prop._offers[offer_idx]
                        if offer.status == 'pending':
                            action = input("Accept or refuse this offer? (a/r): ").lower()
                            if action == 'a':
                                offer.action_accept()
                            elif action == 'r':
                                offer.action_refuse()
                            else:
                                print("Invalid action.")
                        else:
                            print(f"This offer is already {offer.status}.")
                    else:
                        print("Invalid offer number.")
                else:
                    print("Invalid property number.")
            except ValueError:
                print("Please enter a valid number.")
        
        elif choice == '6':
            # View property types
            print("\nProperty Types:")
            for i, t in enumerate(property_types, 1):
                print(f"{i}. {t.name}")
                
            # Count properties by type
            type_counts = {}
            for prop in properties:
                if prop.property_type_id:
                    type_counts[prop.property_type_id] = type_counts.get(prop.property_type_id, 0) + 1
            
            print("\nProperty Count by Type:")
            for t in property_types:
                count = type_counts.get(t.id, 0)
                print(f"{t.name}: {count} properties")
        
        elif choice == '7':
            # View property tags
            print("\nProperty Tags:")
            for i, tag in enumerate(property_tags, 1):
                print(f"{i}. {tag.name}")
                
            # Count properties by tag
            tag_counts = {}
            for prop in properties:
                for tag_id in prop.tag_ids:
                    tag_counts[tag_id] = tag_counts.get(tag_id, 0) + 1
            
            print("\nProperty Count by Tag:")
            for tag in property_tags:
                count = tag_counts.get(tag.id, 0)
                print(f"{tag.name}: {count} properties")
        
        elif choice == '8':
            # Exit
            print("\nThank you for using the Real Estate Management Demo!")
            break
            
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    interactive_demo()