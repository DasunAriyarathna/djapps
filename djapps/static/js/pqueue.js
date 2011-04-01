

function PriorityQueue(cmp_func)
{
    /**
     * Clears the priority queue.
     */
    this.clear = function()
    {
        this.length     = 0;
        this.entries    = [null];
    };

    /**
     * Return the number of entries in the PQ.
     */
    this.size   =   function()
    {
        return this.length;
    };

    /**
     * Returns true if the queue is empty,
     * false otherwise.
     */
    this.empty  =   function()
    {
        return this.length == 0;
    };

    /**
     * Adds a new item to the queue.  Priority is calculated using the
     * comparator function (which if null results in a natural ordering)
     */
    this.add        = function(value)
    {
        this.entries[++this.length] = value;
        this._upheap(this.length);
    };

    /**
     * Returns, without removing, the item with the highest priority.
     */
    this.peek       = function()
    {
        return this.length == 0 ? null : this.entries[0];
    };

    /**
     * Removes and returns the highest priority item.
     */
    this.pop        = function()
    {
        var out = this.entries[1];
        this.entries[1] = this.entries[this.length--];
        this._downheap(1);
        return out;
    };

    /**
     * Get the priority of a given object.
     *
     * Highest priority has the lowest value.  This can be directly used to
     * fetch the appropriate item.
     */
    this.get_priority   = function(value, eq_func)
    {
        if (eq_func != undefined && eq_func != null)
        {
            for (var i = 1;i <= this.length;i++)
            {
                if (eq_func(this.entries[i], value))
                    return i;
            }
        }
        else
        {
            for (var i = 1;i <= this.length;i++)
            {
                if (this.entries[i] == value)
                    return i;
            }
        }
        return -1;
    };

    /**
     * Get the item at a given priority.  This priority could have been
     * optained from the get_priority function.
     *
     * Highest priority has the lowest value.  This can be directly used to
     * fetch the appropriate item.
     */
    this.get_at_priority    = function(priority)
    {
        return this.entries[priority];
    };

    /**
     * Replace the value at a given priority.
     */
    this.replace            = function(value, index /* = 1 */)
    {
        if (index == undefined && index == null)
            index = 1;

        var old = this.entries[index];
        this.entries[index] = value;

        // does the new item have a higher, lower or same priority?
        var cmp = this._comparator(value, old)

        if (cmp < 0)
        {
            this._downheap(index);
        }
        else if (cmp > 0)
        {
            this._upheap(index);
        }
    };

    /**
     * Performs an upheap after an insertion.
     */
    this._upheap    = function(index)
    {
        var changed = false;
        var v       = this.entries[index];
        this.entries[0] = null;
        var i2 = Math.floor(index / 2);
        while (i2 > 0 && this._comparator(this.entries[i2], v) < 0)
        {
            this.entries[index] = this.entries[i2];
            index               = Math.floor(index / 2);
            i2                  = Math.floor(index / 2);
            changed             = true;
        }
        this.entries[index] = v;
        return changed;
    };

    /**
     * performs a downheap after a deletion or replacement.
     */
    this._downheap  = function(index)
    {
        var changed = false;
        var v       = this.entries[index];
        while (index <= Math.floor(this.length / 2))
        {
            var j = index + index;
            if (j == 0)
                j++
            if (j < this.length && this._comparator(this.entries[j], this.entries[j + 1]) < 0)
                j++;
            if (this._comparator(v, this.entries[j]) >= 0)
                break ;
            this.entries[index] = this.entries[j];
            index = j;
            changed = true;
        }
        this.entries[index] = v;
        return changed;
    };

    this.clear();
    this._comparator = cmp_func;

    if (this._comparator == null)
    {
        this._comparator = function(a, b)
        {
            return a - b;
        };
    }
}
