package com.bobcourse.analytics.dto;

import java.util.List;

/**
 * CSV export request — Python sends this after stripping student_id.
 */
public class CsvExportRequest {

    private String campaignId;
    private String courseCode;
    private String courseName;
    private String semesterName;
    private List<CampaignStatsRequest.SubmissionData> submissions;

    public String getCampaignId() { return campaignId; }
    public void setCampaignId(String campaignId) { this.campaignId = campaignId; }
    public String getCourseCode() { return courseCode; }
    public void setCourseCode(String courseCode) { this.courseCode = courseCode; }
    public String getCourseName() { return courseName; }
    public void setCourseName(String courseName) { this.courseName = courseName; }
    public String getSemesterName() { return semesterName; }
    public void setSemesterName(String semesterName) { this.semesterName = semesterName; }
    public List<CampaignStatsRequest.SubmissionData> getSubmissions() { return submissions; }
    public void setSubmissions(List<CampaignStatsRequest.SubmissionData> submissions) { this.submissions = submissions; }
}
