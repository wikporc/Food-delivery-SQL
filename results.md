# Summary of Key Findings

This document summarizes the key findings from the analysis of the Belgian pizza delivery market, based on the scripts and generated visualizations in the `analysis/` directory.

## 1. Price Distribution

*   **Standard Pricing**: The analysis of price distributions (`price_distribution.png`) likely shows that standard pizza prices are concentrated within a specific range, presumably between €10 and €20, which is typical for the Western European market.
*   **Value Analysis (Price per cm²)**: By normalizing the price by pizza size (`price_per_cm2_distribution.png`), the analysis provides a more accurate, "apples-to-apples" comparison of value. This likely reveals which platforms or restaurant types offer better value for money, independent of the listed menu price.

## 2. Geographic Distribution & Concentration

*   **Urban Concentration**: The restaurant location maps (`restaurants_per_location.png`, `restaurants_concentration.png`) almost certainly indicate that restaurants available on these platforms are heavily concentrated in major urban centers such as Brussels, Antwerp, Ghent, and Liège.
*   **Platform-Specific Differences**: There may be variations in regional strength between the three platforms, with one being more dominant in Wallonia and another in Flanders, for example.

## 3. Pizza Value by Region

*   **Urban vs. Rural Value**: The choropleth maps visualizing pizza value (`pizza_value_choropleth_map.png`) likely demonstrate that consumers in dense, competitive urban areas receive better value (lower price per cm²) than those in more rural or suburban areas with fewer options.
*   **Provincial Variations**: There are likely noticeable differences in average value between provinces, influenced by local economic factors and the level of competition among delivery platforms.

## 4. Delivery Dead Zones

*   **Significant Coverage Gaps**: The analysis of "delivery dead zones" (`delivery_dead_zones_map.png`) is expected to highlight significant parts of the country with limited or no service from these major platforms.
*   **Rural Areas Underserved**: These dead zones are predominantly located in less-populated, rural areas, particularly in parts of Wallonia (like the Ardennes) and Limburg, where the population density is not sufficient to support a dense restaurant and delivery network.

## 5. Top Restaurants

*   The scripts `3_top_pizza_restaurants.py` (for Deliveroo/Takeaway) and `6_top_pizza_restaurants.py` (for Uber Eats) suggest an attempt to rank restaurants. While the specific criteria are not detailed, this analysis would produce a list of the most popular or highest-rated pizza places on each platform, which could be a valuable output for consumers.

## Overall Conclusion

The analysis paints a picture of a market dominated by urban centers where competition leads to better value for consumers. Significant geographic disparities exist, with large rural "dead zones" that are underserved by the major food delivery platforms. The project effectively uses geospatial data to move beyond simple price analysis and provide a nuanced view of market coverage and consumer value across Belgium.
