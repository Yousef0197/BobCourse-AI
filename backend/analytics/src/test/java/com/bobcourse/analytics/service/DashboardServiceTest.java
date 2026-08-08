package com.bobcourse.analytics.service;

import com.bobcourse.analytics.dto.DashboardRequest;
import com.bobcourse.analytics.dto.DashboardResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.Collections;

import static org.junit.jupiter.api.Assertions.*;

class DashboardServiceTest {

    private DashboardService service;

    @BeforeEach
    void setUp() {
        service = new DashboardService();
    }

    private DashboardRequest.CampaignSummary camp(String id, String status, int subs, int enrolled, double avg) {
        DashboardRequest.CampaignSummary c = new DashboardRequest.CampaignSummary();
        c.setCampaignId(id);
        c.setStatus(status);
        c.setSubmissions(subs);
        c.setEnrolled(enrolled);
        c.setAverageRating(avg);
        return c;
    }

    @Test
    void computeKnownInputs_correctKPIs() {
        DashboardRequest req = new DashboardRequest();
        req.setTotalEnrolled(60);
        req.setCampaigns(Arrays.asList(
                camp("c1", "open", 20, 30, 4.0),
                camp("c2", "closed", 25, 30, 3.6)
        ));

        DashboardResponse resp = service.compute(req);

        assertEquals(2, resp.getTotalCampaigns());
        assertEquals(1, resp.getActiveCampaigns()); // only c1 is open
        assertEquals(45, resp.getTotalSubmissions());
        // weighted avg = (4.0*20 + 3.6*25) / 45 = (80 + 90) / 45 = 170/45 ≈ 3.78
        assertEquals(3.78, resp.getAverageRating(), 0.01);
        // response rate = 45/60 = 75%
        assertEquals(75.0, resp.getOverallResponseRate(), 0.01);
    }

    @Test
    void computeNoCampaigns_returnsZeros() {
        DashboardRequest req = new DashboardRequest();
        req.setTotalEnrolled(100);
        req.setCampaigns(Collections.emptyList());

        DashboardResponse resp = service.compute(req);
        assertEquals(0, resp.getTotalCampaigns());
        assertEquals(0, resp.getActiveCampaigns());
        assertEquals(0.0, resp.getAverageRating());
        assertEquals(0.0, resp.getOverallResponseRate());
    }

    @Test
    void computeAllClosed_zeroActiveCampaigns() {
        DashboardRequest req = new DashboardRequest();
        req.setTotalEnrolled(50);
        req.setCampaigns(Arrays.asList(
                camp("c1", "closed", 20, 25, 4.2),
                camp("c2", "closed", 22, 25, 3.8)
        ));

        DashboardResponse resp = service.compute(req);
        assertEquals(0, resp.getActiveCampaigns());
        assertEquals(2, resp.getTotalCampaigns());
    }
}
