package com.bobcourse.analytics.dto;

import java.util.List;

/**
 * Request for multi-semester trend data.
 * Contains per-semester campaign stats.
 */
public class TrendRequest {

    private String courseCode;
    private String courseName;
    private List<SemesterData> semesters;

    public static class SemesterData {
        private String semesterId;
        private String semesterName;
        private int year;
        private double overallAverage;
        private int totalSubmissions;
        private int totalEnrolled;

        public String getSemesterId() { return semesterId; }
        public void setSemesterId(String semesterId) { this.semesterId = semesterId; }
        public String getSemesterName() { return semesterName; }
        public void setSemesterName(String semesterName) { this.semesterName = semesterName; }
        public int getYear() { return year; }
        public void setYear(int year) { this.year = year; }
        public double getOverallAverage() { return overallAverage; }
        public void setOverallAverage(double overallAverage) { this.overallAverage = overallAverage; }
        public int getTotalSubmissions() { return totalSubmissions; }
        public void setTotalSubmissions(int totalSubmissions) { this.totalSubmissions = totalSubmissions; }
        public int getTotalEnrolled() { return totalEnrolled; }
        public void setTotalEnrolled(int totalEnrolled) { this.totalEnrolled = totalEnrolled; }
    }

    public String getCourseCode() { return courseCode; }
    public void setCourseCode(String courseCode) { this.courseCode = courseCode; }
    public String getCourseName() { return courseName; }
    public void setCourseName(String courseName) { this.courseName = courseName; }
    public List<SemesterData> getSemesters() { return semesters; }
    public void setSemesters(List<SemesterData> semesters) { this.semesters = semesters; }
}
