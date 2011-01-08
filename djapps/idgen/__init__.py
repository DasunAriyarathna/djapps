"""
This module allows one to create unique but random IDs for use with objects
in a DB.  This is great when you dont want IDs that are sequential (which
can be easily regenerated and hence scraped).  We do this with linear
feedback shift registers.
"""
