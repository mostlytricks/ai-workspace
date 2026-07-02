package com.legacy.mart.order;

public class OrderDto {
    private long orderId;
    private long customerId;
    private String sku;
    private String status;
    private boolean inStock;

    public long getOrderId() { return orderId; }
    public void setOrderId(long orderId) { this.orderId = orderId; }
    public long getCustomerId() { return customerId; }
    public void setCustomerId(long customerId) { this.customerId = customerId; }
    public String getSku() { return sku; }
    public void setSku(String sku) { this.sku = sku; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public boolean isInStock() { return inStock; }
    public void setInStock(boolean inStock) { this.inStock = inStock; }
}
