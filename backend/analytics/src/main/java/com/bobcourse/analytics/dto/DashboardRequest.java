package com.bobcourse.analytics.dto;

import java.util.List;

/**
 * Request for university-wide dashboard KPIs.
 */
public class DashboardRequest {

    private int totalEnrolled;
    private List<CampaignSummary> campaigns;

    public static class CampaignSummary {
        private String campaignId;
        private String status;
        private int submissions;
        private int enrolled;
        private double averageRating;

        public String getCampaignId() { return campaignId; }
        public void setCampaignId(String campaignId) { this.campaignId = campaignId; }
        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }
        public int getSubmissions() { return submissions; }
        public void setSubmissions(int submissions) { this.submissions = submissions; }
        public int getEnrolled() { return enrolled; }
        public void setEnrolled(int enrolled) { this.enrolled = enrolled; }
        public double getAverageRating() { return averageRating; }
        public void setAverageRating(double averageRating) { this.averageRating = averageRating; }
    }

    public int getTotalEnrolled() { return totalEnrolled; }
    public void setTotalEnrolled(int totalEnrolled) { this.totalEnrolled = totalEnrolled; }
    public List<CampaignSummary> getCampaigns() { return campaigns; }
    public void setCampaigns(List<CampaignSummary> campaigns) { this.campaigns = campaigns; }
}
