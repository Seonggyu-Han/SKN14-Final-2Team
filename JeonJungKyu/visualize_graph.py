# visualize_graph.py
from main import app
import os

def save_graph_visualization():
    """그래프를 이미지로 저장"""
    try:
        # Mermaid PNG 생성
        img_data = app.get_graph().draw_mermaid_png()
        
        with open("perfume_bot_graph.png", "wb") as f:
            f.write(img_data)
        
        print("✅ 그래프가 'perfume_bot_graph.png'로 저장되었습니다!")
        
        # 파일이 실제로 생성되었는지 확인
        if os.path.exists("perfume_bot_graph.png"):
            size = os.path.getsize("perfume_bot_graph.png")
            print(f"📁 파일 크기: {size:,} bytes")
        
    except Exception as e:
        print(f"❌ 시각화 오류: {e}")

def save_graph_mermaid():
    """Mermaid 코드를 텍스트로 저장"""
    try:
        mermaid_code = app.get_graph().draw_mermaid()
        
        with open("perfume_bot_graph.mmd", "w", encoding="utf-8") as f:
            f.write(mermaid_code)
        
        print("✅ Mermaid 코드가 'perfume_bot_graph.mmd'로 저장되었습니다!")
        print("🌐 https://mermaid.live 에서 시각화할 수 있습니다.")
        
        # 코드도 출력
        print("\n📝 Mermaid 코드:")
        print("-" * 40)
        print(mermaid_code)
        print("-" * 40)
        
    except Exception as e:
        print(f"❌ Mermaid 생성 오류: {e}")

def print_detailed_graph_info():
    """상세한 그래프 정보 출력"""
    try:
        graph = app.get_graph()
        
        print("📊 상세 그래프 정보:")
        print(f"노드 수: {len(graph.nodes)}")
        print(f"엣지 수: {len(graph.edges)}")
        
        print("\n🔗 노드 목록:")
        for node_id, node_data in graph.nodes.items():
            print(f"  - {node_id}: {type(node_data).__name__}")
        
        print("\n➡️ 엣지 목록:")
        for edge in graph.edges:
            print(f"  - {edge}")
            
        print("\n🎯 시작점:", graph.first_node)
        
    except Exception as e:
        print(f"❌ 그래프 정보 오류: {e}")

if __name__ == "__main__":
    print("🎨 향수 봇 그래프 시각화")
    print("=" * 40)
    
    print("1. PNG 이미지로 저장")
    print("2. Mermaid 코드로 저장") 
    print("3. 그래프 정보 보기")
    print("4. 모두 실행")
    
    choice = input("선택 (1-4): ").strip()
    
    if choice == "1":
        save_graph_visualization()
    elif choice == "2":
        save_graph_mermaid()
    elif choice == "3":
        print_detailed_graph_info()
    elif choice == "4":
        save_graph_visualization()
        save_graph_mermaid() 
        print_detailed_graph_info()
    else:
        print("잘못된 선택입니다. 모두 실행합니다.")
        save_graph_visualization()
        save_graph_mermaid()
        print_detailed_graph_info()