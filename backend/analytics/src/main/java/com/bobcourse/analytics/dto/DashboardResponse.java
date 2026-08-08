package com.bobcourse.analytics.dto;

/**
 * University-wide KPI dashboard response.
 */
public class DashboardResponse {

    private int totalCampaigns;
    private int activeCampaigns;
    private int totalSubmissions;
    private double averageRating;
    private double overallResponseRate;

    public int getTotalCampaigns() { return totalCampaigns; }
    public void setTotalCampaigns(int totalCampaigns) { this.totalCampaigns = totalCampaigns; }
    public int getActiveCampaigns() { return activeCampaigns; }
    public void setActiveCampaigns(int activeCampaigns) { this.activeCampaigns = activeCampaigns; }
    public int getTotalSubmissions() { return totalSubmissions; }
    public void setTotalSubmissions(int totalSubmissions) { this.totalSubmissions = totalSubmissions; }
    public double getAverageRating() { return averageRating; }
    public void setAverageRating(double averageRating) { this.averageRating = averageRating; }
    public double getOverallResponseRate() { return overallResponseRate; }
    public void setOverallResponseRate(double overallResponseRate) { this.overallResponseRate = overallResponseRate; }
}
