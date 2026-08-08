package com.bobcourse.analytics.dto;

import java.util.List;
import java.util.Map;

/**
 * Response for campaign statistics — returned to Python, then forwarded to the frontend.
 */
public class CampaignStatsResponse {

    private String campaignId;
    private String courseCode;
    private String courseName;
    private int totalSubmissions;
    private int totalEnrolled;
    private double responseRate;
    private double overallAverage;
    private List<QuestionStats> questionStats;

    // ── Nested ──────────────────────────────────────────────────────────────
    public static class QuestionStats {
        private String questionId;
        private String questionText;
        private double average;
        private Map<Integer, Long> distribution; // rating → count

        public String getQuestionId() { return questionId; }
        public void setQuestionId(String questionId) { this.questionId = questionId; }
        public String getQuestionText() { return questionText; }
        public void setQuestionText(String questionText) { this.questionText = questionText; }
        public double getAverage() { return average; }
        public void setAverage(double average) { this.average = average; }
        public Map<Integer, Long> getDistribution() { return distribution; }
        public void setDistribution(Map<Integer, Long> distribution) { this.distribution = distribution; }
    }

    // ── Getters / Setters ───────────────────────────────────────────────────
    public String getCampaignId() { return campaignId; }
    public void setCampaignId(String campaignId) { this.campaignId = campaignId; }
    public String getCourseCode() { return courseCode; }
    public void setCourseCode(String courseCode) { this.courseCode = courseCode; }
    public String getCourseName() { return courseName; }
    public void setCourseName(String courseName) { this.courseName = courseName; }
    public int getTotalSubmissions() { return totalSubmissions; }
    public void setTotalSubmissions(int totalSubmissions) { this.totalSubmissions = totalSubmissions; }
    public int getTotalEnrolled() { return totalEnrolled; }
    public void setTotalEnrolled(int totalEnrolled) { this.totalEnrolled = totalEnrolled; }
    public double getResponseRate() { return responseRate; }
    public void setResponseRate(double responseRate) { this.responseRate = responseRate; }
    public double getOverallAverage() { return overallAverage; }
    public void setOverallAverage(double overallAverage) { this.overallAverage = overallAverage; }
    public List<QuestionStats> getQuestionStats() { return questionStats; }
    public void setQuestionStats(List<QuestionStats> questionStats) { this.questionStats = questionStats; }
}
