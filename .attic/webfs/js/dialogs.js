
// 
// General dialog functionality - modal and non-modal ones
//

// 
// Dialog listener interface
//
function DLGListener()
{
    // Called after a button is pressed.  All buttons have the effect of
    // closing the dialog.
    //
    // If this function returns false, the button press is ignored and the
    // dialog is NOT closed.
    this.ButtonPressed = function(dlg, btnname) { return true; }
}

// 
// Creates a dialog
//
function Dialog(listener, config)
{
    // gets the content area on which other 
    // controls can be embedded
    this.GetContentHolder = function() 
    {
        return this.contentHolder;
    }

    // is the dialog showing?
    this.IsShowing = function()
    {
        return this.isShowing;
    }

    // Show or hide the dialog
    this.Show = function(visible)
    {
        this.isShowing = visible;
        if (visible)
        {
            this.parent.style.visibility = "visible";
        }
        else
        {
            this.mainDiv.style.visibility    = "none";
            this.mainDiv.style.display       = "none";
        }

        // var win = window;
        // window.styles['background-color'] = "black";
    }

    // Initialises the dialog
    this._initialise = function(listener, config)
    {
        if (typeof(parent) == "string")
        {
            this.parent         = ElementById(parent);
        }
        else
        {
            this.parent         = parent;
        }

        this.mainDiv        = CreateDiv(null,
                               {position: 'absolute',
                                'background-color': 'black',
                                visibility: 'visible',
                                left: 0, top: 0, width: '100%', height: '100%'
                               });
        this.contentHolder  = CreateDiv(null, {left: 50, top: 50, visibility: 'visible'}, this.mainDiv);
    }

    this._initialise(listener, config);
}

