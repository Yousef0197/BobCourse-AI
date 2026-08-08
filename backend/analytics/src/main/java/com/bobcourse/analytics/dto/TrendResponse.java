package com.bobcourse.analytics.dto;

import java.util.List;

/**
 * Response for multi-semester trends.
 */
public class TrendResponse {

    private String courseCode;
    private String courseName;
    private List<TrendPoint> trendPoints;
    private Double trendSlope; // positive = improving, negative = declining

    public static class TrendPoint {
        private String semesterName;
        private int year;
        private double averageRating;
        private double responseRate;
        private int submissions;

        public String getSemesterName() { return semesterName; }
        public void setSemesterName(String semesterName) { this.semesterName = semesterName; }
        public int getYear() { return year; }
        public void setYear(int year) { this.year = year; }
        public double getAverageRating() { return averageRating; }
        public void setAverageRating(double averageRating) { this.averageRating = averageRating; }
        public double getResponseRate() { return responseRate; }
        public void setResponseRate(double responseRate) { this.responseRate = responseRate; }
        public int getSubmissions() { return submissions; }
        public void setSubmissions(int submissions) { this.submissions = submissions; }
    }

    public String getCourseCode() { return courseCode; }
    public void setCourseCode(String courseCode) { this.courseCode = courseCode; }
    public String getCourseName() { return courseName; }
    public void setCourseName(String courseName) { this.courseName = courseName; }
    public List<TrendPoint> getTrendPoints() { return trendPoints; }
    public void setTrendPoints(List<TrendPoint> trendPoints) { this.trendPoints = trendPoints; }
    public Double getTrendSlope() { return trendSlope; }
    public void setTrendSlope(Double trendSlope) { this.trendSlope = trendSlope; }
}
