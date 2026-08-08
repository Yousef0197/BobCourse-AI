package com.bobcourse.analytics.service;

import com.bobcourse.analytics.dto.TrendRequest;
import com.bobcourse.analytics.dto.TrendResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.Collections;

import static org.junit.jupiter.api.Assertions.*;

class TrendServiceTest {

    private TrendService service;

    @BeforeEach
    void setUp() {
        service = new TrendService();
    }

    private TrendRequest.SemesterData sem(String name, int year, double avg, int subs, int enrolled) {
        TrendRequest.SemesterData sd = new TrendRequest.SemesterData();
        sd.setSemesterId("sem-" + year);
        sd.setSemesterName(name);
        sd.setYear(year);
        sd.setOverallAverage(avg);
        sd.setTotalSubmissions(subs);
        sd.setTotalEnrolled(enrolled);
        return sd;
    }

    @Test
    void computeImprovingTrend_positiveSlopeCourse() {
        TrendRequest req = new TrendRequest();
        req.setCourseCode("CS101");
        req.setCourseName("Intro CS");
        req.setSemesters(Arrays.asList(
                sem("Fall 2022", 2022, 3.0, 20, 25),
                sem("Spring 2023", 2023, 3.5, 22, 25),
                sem("Fall 2023", 2023, 4.0, 23, 25)
        ));

        TrendResponse resp = service.compute(req);
        assertEquals(3, resp.getTrendPoints().size());
        assertTrue(resp.getTrendSlope() > 0, "Improving trend should have positive slope");
        assertEquals("Fall 2022", resp.getTrendPoints().get(0).getSemesterName());
        assertEquals(3.0, resp.getTrendPoints().get(0).getAverageRating(), 0.01);
    }

    @Test
    void computeDecliningTrend_negativeSlopeExpected() {
        TrendRequest req = new TrendRequest();
        req.setCourseCode("CS201");
        req.setCourseName("Data Structures");
        req.setSemesters(Arrays.asList(
                sem("Fall 2022", 2022, 4.5, 20, 25),
                sem("Spring 2023", 2023, 4.0, 22, 25),
                sem("Fall 2023", 2023, 3.5, 23, 25)
        ));

        TrendResponse resp = service.compute(req);
        assertTrue(resp.getTrendSlope() < 0, "Declining trend should have negative slope");
    }

    @Test
    void computeEmptySemesters_returnsZeroSlope() {
        TrendRequest req = new TrendRequest();
        req.setCourseCode("CS301");
        req.setCourseName("Algorithms");
        req.setSemesters(Collections.emptyList());

        TrendResponse resp = service.compute(req);
        assertEquals(0.0, resp.getTrendSlope());
        assertTrue(resp.getTrendPoints().isEmpty());
    }

    @Test
    void computeResponseRate_correctlyComputed() {
        TrendRequest req = new TrendRequest();
        req.setCourseCode("CS401");
        req.setCourseName("OS");
        req.setSemesters(Collections.singletonList(sem("Fall 2024", 2024, 4.0, 15, 20)));

        TrendResponse resp = service.compute(req);
        assertEquals(75.0, resp.getTrendPoints().get(0).getResponseRate(), 0.01);
    }
}
