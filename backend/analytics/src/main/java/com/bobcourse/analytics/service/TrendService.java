package com.bobcourse.analytics.service;

import com.bobcourse.analytics.dto.TrendRequest;
import com.bobcourse.analytics.dto.TrendResponse;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

/**
 * TrendService — computes multi-semester trend data and linear slope.
 */
@Service
public class TrendService {

    public TrendResponse compute(TrendRequest request) {
        TrendResponse response = new TrendResponse();
        response.setCourseCode(request.getCourseCode());
        response.setCourseName(request.getCourseName());

        List<TrendRequest.SemesterData> semesters = request.getSemesters();
        if (semesters == null || semesters.isEmpty()) {
            response.setTrendPoints(new ArrayList<>());
            response.setTrendSlope(0.0);
            return response;
        }

        List<TrendResponse.TrendPoint> points = new ArrayList<>();
        for (TrendRequest.SemesterData sd : semesters) {
            TrendResponse.TrendPoint point = new TrendResponse.TrendPoint();
            point.setSemesterName(sd.getSemesterName());
            point.setYear(sd.getYear());
            point.setAverageRating(Math.round(sd.getOverallAverage() * 100.0) / 100.0);
            point.setResponseRate(sd.getTotalEnrolled() > 0
                    ? Math.round((double) sd.getTotalSubmissions() / sd.getTotalEnrolled() * 10000.0) / 100.0
                    : 0.0);
            point.setSubmissions(sd.getTotalSubmissions());
            points.add(point);
        }
        response.setTrendPoints(points);

        // Linear regression slope on averageRating over index
        response.setTrendSlope(computeSlope(points));

        return response;
    }

    /**
     * Simple linear regression slope: positive = improving over time.
     */
    private double computeSlope(List<TrendResponse.TrendPoint> points) {
        int n = points.size();
        if (n < 2) return 0.0;

        double sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
        for (int i = 0; i < n; i++) {
            double x = i;
            double y = points.get(i).getAverageRating();
            sumX += x;
            sumY += y;
            sumXY += x * y;
            sumX2 += x * x;
        }

        double denom = n * sumX2 - sumX * sumX;
        if (denom == 0) return 0.0;

        double slope = (n * sumXY - sumX * sumY) / denom;
        return Math.round(slope * 1000.0) / 1000.0;
    }
}
