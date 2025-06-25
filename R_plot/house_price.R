library(sf)
library(ggplot2)
library(rayshader)

# 读取并处理数据
data <- read.csv('data/processed/communities/communities_filtered.csv')
data <- data[,c('PRI', 'longitude', 'latitude')]
data_sf <- st_as_sf(data, coords = c("longitude", "latitude"), crs = 4326)
data$PRI <- as.numeric(data$PRI)
summary(data_sf$PRI)

# 加载广州市地图数据
gz_map <- st_read("data/raw/center_city/广州市.shp")
gz_map <- st_transform(gz_map, st_crs(data_sf))


# 创建 ggplot 对象
p <- ggplot() +
  geom_sf(data = gz_map,linetype = "blank") +  
  geom_point(data = data, aes(x = longitude, y = latitude, color = PRI),size = 3, alpha = 0.5) +  # 透明度alpha设为合适的值，比如0.8，避免过高影响可视化效果
  scale_color_gradientn(colours = viridis::plasma(10)) +
  coord_sf() +
  theme_minimal() +
  # 添加图形的标题以及坐标轴等相关标签
  labs(title = "Canton House Price Distribution",x='',y='', color = "")+
  theme(title = element_text(size = 20),
        axis.text = element_text(size = 8),  # 坐标轴刻度标签字体大小设为12
        legend.text = element_text(size = 10),  # 图例标签字体大小设为12
        legend.title = element_text(size = 14),
        legend.position = "right") 
p

# 将 ggplot 转换为 3D 图像
plot_3d <- plot_gg(p,
                   height_aes = 'color',
                   width = 9,
                   height = 7,
                   scale = 900,
                   windowsize = c(1200, 900),
                   offset_edges = 1,
                   pointcontract = 0.9,
)

render_camera(zoom = 0.5, theta = -4, phi = 65)

# 使用render_snapshot保存图片，默认保存为png格式，文件名为当前日期时间戳组成的字符串
render_snapshot("figures/gz_center_price_3d_t.png")
