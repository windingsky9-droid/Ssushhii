export const SERVER_NAME = "birth-sky-mcp-server";
export const SERVER_VERSION = "1.0.0";

/** URI of the chart-wheel view rendered by MCP Apps hosts. */
export const VIEW_URI = "ui://birth-sky/chart-view.html";

/** Responses longer than this are trimmed with a note on how to page or filter. */
export const CHARACTER_LIMIT = 25000;

/** Years where the ephemeris stays within a few arcminutes. */
export const MIN_YEAR = 1900;
export const MAX_YEAR = 2100;

export const PRECISION_NOTE =
  "Positions come from a low-precision analytic ephemeris (Schlyter), accurate to about 2′ for the Sun and Moon and within about 6′ for the planets between 1900 and 2100. Event times are good to roughly 15 minutes for the Moon and a few hours for slow planets.";
