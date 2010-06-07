
/**
 * This module enables equation editing on a canvas in an html page.
 * Following are the features:
 *  1. Equations are presented in multiple lines or be single line only.
 *  2. Equations may be aligned at a certain point (say => or -> or =).
 *  3. Allow custom characters (eg alpha, delta etc) and container objects
 *     (eg summations, integrals, roots etc).
 *  4. Allow multiple formattings on characters and so on, so rendering can
 *     be affected by it.
 *  5. Allow selection and highlighting by mouse and entering data by
 *     keyboard or mouse.
 *  6. Enable mulitple elements in a page (so easy to access each with the
 *     same controller).
 *  7. Semantic analysis to be possible - eg take a line and convert it to
 *     an equation object to be sent to server.
 */

/**
 * A node in the equation tree.
 */
function EqnNode()
{
    /**
     * Can this node be navigated?
     */
    this.navigateable   = true;

    /**
     * Renders the node.
     */
    this.renderFunc = null;
}

/**
 * Class for calculating the size of a node's size.
 */
function EqnNodeSizeCalculator()
{
    /**
     * Calculate the node's width and height.
     */
    this.getWidth   = function(node) { return 0; }
    this.getHeight  = function(node) { return 0; }
}

/**
 * Render's a node onto a context.
 */
function EqnNodeRenderer()
{
    this.render = function(node, x, y) {
    }
}

/**
 * Leafs in the equation tree.
 */
function EqnLeaf()
{
    // type - operator, number, id, variable - defined and wont change
    this.leafType   = 0;
    this.leafValue  = null;
}

/**
 * Container items in the equation tree.  These are very dynamic and we can
 * add new ones along with their behavours.
 */
function EqnContainer()
{
    /**
     * The child nodes in this equation.
     */
    this.children   = [];
}

/**
 * Create a new editor with the ID of the canvas element to create with.
 */
function EquationEditor(canvasid)
{
    // Current line number
    this.currentLine    = -1;

    // Scroll offsets
    this.scrollX        = 0;
    this.scrollY        = 0;
    this.canvasid       = canvasid;
    this.drawingCanvas  = document.getElementById(canvasid);
    this.context        = null;
    // check the element is in the DOM and the browser supports canvas.
    if (drawingCanvas.getContext)
    {
        this.context = drawingCanvas.getContext('2d');

        // Create the yellow face
        /*
        context.strokeStyle = "#000000";
        context.fillStyle = "#FFFF00";
        context.beginPath();
        context.arc(100,100,50,0,Math.PI*2,true);
        context.closePath();
        context.stroke();
        context.fill();
        return context;
        */
    }
}

