
/**
 * Module for parsing mathematica expressions and returns a common js
 * format that we can send to the backend.
 *
 * We want the parsing to be incremental so we can just give a character at
 * a time and see what is happening.  This will allow us do things like
 * intellisense if necessary by seeing see when the last token was typed
 * etc.
 */

// The mathematica namespace
var TOKEN_COUNT         = 0;
var TOKEN_COMMENT       = new MatikaToken(TOKEN_COUNT++, "<COMMENT>");
var TOKEN_SPACE         = new MatikaToken(TOKEN_COUNT++, "<SPACE>");
var TOKEN_NUMBER        = new MatikaToken(TOKEN_COUNT++, "<NUM>");
var TOKEN_STRING        = new MatikaToken(TOKEN_COUNT++, "<STRING>");
var TOKEN_IDENT         = new MatikaToken(TOKEN_COUNT++, "<IDENT>");
var TOKEN_OPEN_SQ       = new MatikaToken(TOKEN_COUNT++, "[");
var TOKEN_CLOSE_SQ      = new MatikaToken(TOKEN_COUNT++, "]");
var TOKEN_OPEN_PAREN    = new MatikaToken(TOKEN_COUNT++, "(");
var TOKEN_CLOSE_PAREN   = new MatikaToken(TOKEN_COUNT++, ")");
var TOKEN_OPEN_BRACE    = new MatikaToken(TOKEN_COUNT++, "{");
var TOKEN_CLOSE_BRACE   = new MatikaToken(TOKEN_COUNT++, "}");
var TOKEN_COMA          = new MatikaToken(TOKEN_COUNT++, ",");
var TOKEN_OP_PLUS       = new MatikaToken(TOKEN_COUNT++, "+");
var TOKEN_OP_MINUS      = new MatikaToken(TOKEN_COUNT++, "-");
var TOKEN_OP_MULT       = new MatikaToken(TOKEN_COUNT++, "*");
var TOKEN_OP_DIV        = new MatikaToken(TOKEN_COUNT++, "/");
var TOKEN_OP_POW        = new MatikaToken(TOKEN_COUNT++, "^");
var TOKEN_OP_COLCOL     = new MatikaToken(TOKEN_COUNT++, "::");
var TOKEN_OP_INCR       = new MatikaToken(TOKEN_COUNT++, "++");
var TOKEN_OP_DECR       = new MatikaToken(TOKEN_COUNT++, "--");
var TOKEN_OP_MAP        = new MatikaToken(TOKEN_COUNT++, "<Map>");
var TOKEN_OP_FACT       = new MatikaToken(TOKEN_COUNT++, "!");
var TOKEN_OP_FACT2      = new MatikaToken(TOKEN_COUNT++, "!!");
var TOKEN_OP_DERIV      = new MatikaToken(TOKEN_COUNT++, "'");
var TOKEN_OP_STRJOIN    = new MatikaToken(TOKEN_COUNT++, "<>");
var TOKEN_OP_LOR        = new MatikaToken(TOKEN_COUNT++, "||");
var TOKEN_OP_LAND       = new MatikaToken(TOKEN_COUNT++, "&&");
var TOKEN_OP_LXOR       = new MatikaToken(TOKEN_COUNT++, "\/");
var TOKEN_OP_EQ         = new MatikaToken(TOKEN_COUNT++, "==");
var TOKEN_OP_NE         = new MatikaToken(TOKEN_COUNT++, "!=");
var TOKEN_OP_GE         = new MatikaToken(TOKEN_COUNT++, ">=");
var TOKEN_OP_GT         = new MatikaToken(TOKEN_COUNT++, ">");
var TOKEN_OP_LE         = new MatikaToken(TOKEN_COUNT++, "<=");
var TOKEN_OP_LT         = new MatikaToken(TOKEN_COUNT++, "<");
var TOKEN_OP_SAMEQ      = new MatikaToken(TOKEN_COUNT++, "===");
var TOKEN_OP_UNSAMEQ    = new MatikaToken(TOKEN_COUNT++, "=!=");
var TOKEN_OP_IMPLIES    = new MatikaToken(TOKEN_COUNT++, "=>");

function MatikaTokenizer()
{
    // current row and column
    this.currRow    = 0;
    // current row and column
    this.currCol    = 0;
}

