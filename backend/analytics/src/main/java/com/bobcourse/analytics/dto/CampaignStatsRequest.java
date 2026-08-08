package com.bobcourse.analytics.dto;

import java.util.List;

/**
 * Request payload sent by Python to compute per-campaign statistics.
 * student_id is intentionally NOT included — Python strips it before calling Java.
 */
public class CampaignStatsRequest {

    private String campaignId;
    private String courseCode;
    private String courseName;
    private int totalEnrolled;
    private List<SubmissionData> submissions;

    // ── Nested DTO ──────────────────────────────────────────────────────────
    public static class SubmissionData {
        private List<AnswerData> answers;

        public List<AnswerData> getAnswers() { return answers; }
        public void setAnswers(List<AnswerData> answers) { this.answers = answers; }
    }

    public static class AnswerData {
        private String questionId;
        private String questionText;
        private int rating;

        public String getQuestionId() { return questionId; }
        public void setQuestionId(String questionId) { this.questionId = questionId; }
        public String getQuestionText() { return questionText; }
        public void setQuestionText(String questionText) { this.questionText = questionText; }
        public int getRating() { return rating; }
        public void setRating(int rating) { this.rating = rating; }
    }

    // ── Getters / Setters ───────────────────────────────────────────────────
    public String getCampaignId() { return campaignId; }
    public void setCampaignId(String campaignId) { this.campaignId = campaignId; }
    public String getCourseCode() { return courseCode; }
    public void setCourseCode(String courseCode) { this.courseCode = courseCode; }
    public String getCourseName() { return courseName; }
    public void setCourseName(String courseName) { this.courseName = courseName; }
    public int getTotalEnrolled() { return totalEnrolled; }
    public void setTotalEnrolled(int totalEnrolled) { this.totalEnrolled = totalEnrolled; }
    public List<SubmissionData> getSubmissions() { return submissions; }
    public void setSubmissions(List<SubmissionData> submissions) { this.submissions = submissions; }
}
