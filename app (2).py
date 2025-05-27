import streamlit as st
import pandas as pd
import io
import plotly.express as px
import streamlit.components.v1 as components
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from collections import Counter
import os
import hashlib
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

# [Previous code remains exactly the same until the tabs section]

        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
            "📊 Note Type Summary", "👨‍🔧 Notes per Technician", "🚨 Top 5 Technicians",
            "🥧 Note Type Distribution", "✅ DONE Terminals", "📑 Detailed Notes", 
            "✍️ Signature Issues", "🔍 Deep Problem Analysis", "🤖 AI Classification"])

        # [Previous tabs 1-8 remain exactly the same]

        with tab9:
            st.markdown("## 🤖 AI-Powered Note Classification")
            
            # Explanation
            st.markdown("""
            This section uses machine learning to automatically cluster and analyze notes:
            - **Clustering**: Groups similar notes together using K-Means algorithm
            - **Similarity**: Finds most representative notes in each cluster
            - **Patterns**: Identifies common phrases and themes
            """)
            
            # AI Classification
            notes = df['NOTE'].fillna("").astype(str)
            
            with st.spinner("Analyzing notes with AI..."):
                # Vectorize the text
                vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
                X = vectorizer.fit_transform(notes)
                
                # Cluster notes
                n_clusters = st.slider("Number of clusters", 3, 10, 5)
                kmeans = KMeans(n_clusters=n_clusters, random_state=42).fit(X)
                df['AI_Cluster'] = kmeans.labels_
                
                # Display clusters
                st.markdown("### 📊 Cluster Distribution")
                cluster_counts = df['AI_Cluster'].value_counts().sort_index()
                fig_clusters = px.bar(cluster_counts, 
                                     labels={'index':'Cluster', 'value':'Count'},
                                     title='Note Clusters Distribution')
                st.plotly_chart(fig_clusters, use_container_width=True)
                
                # Show sample notes from each cluster
                st.markdown("### 🗂️ Sample Notes from Each Cluster")
                for cluster in sorted(df['AI_Cluster'].unique()):
                    with st.expander(f"Cluster {cluster} ({(df['AI_Cluster']==cluster).mean()*100:.1f}%)", expanded=False):
                        cluster_notes = df[df['AI_Cluster']==cluster]['NOTE'].sample(min(5, len(df[df['AI_Cluster']==cluster)))
                        for note in cluster_notes:
                            st.markdown(f"- {note}")
                
                # Find most representative notes
                st.markdown("### 🎯 Most Representative Notes")
                similarity_matrix = cosine_similarity(X)
                most_representative = []
                for cluster in sorted(df['AI_Cluster'].unique()):
                    cluster_indices = df[df['AI_Cluster']==cluster].index
                    cluster_similarity = similarity_matrix[cluster_indices][:, cluster_indices]
                    most_typical_idx = cluster_indices[cluster_similarity.mean(axis=1).argmax()]
                    most_representative.append(df.loc[most_typical_idx, 'NOTE'])
                
                for i, note in enumerate(most_representative):
                    st.markdown(f"""
                    **Cluster {i} Representative:**
                    > {note}
                    """)
                
                # Cluster characteristics
                st.markdown("### 🔍 Cluster Characteristics")
                terms_per_cluster = 10
                feature_names = vectorizer.get_feature_names_out()
                for i in range(n_clusters):
                    centroid = kmeans.cluster_centers_[i]
                    top_terms = [feature_names[ind] for ind in centroid.argsort()[-terms_per_cluster:][::-1]]
                    st.markdown(f"**Cluster {i}**: {', '.join(top_terms)}")
            
            # Download AI analysis
            ai_output = io.BytesIO()
            with pd.ExcelWriter(ai_output, engine='xlsxwriter') as writer:
                df[['NOTE', 'AI_Cluster']].to_excel(writer, sheet_name="AI Classification", index=False)
                cluster_summary = df.groupby('AI_Cluster')['NOTE'].agg(['count', lambda x: x.sample(1).values[0]])
                cluster_summary.columns = ['Count', 'Example Note']
                cluster_summary.to_excel(writer, sheet_name="Cluster Summary")
            
            st.download_button("📥 Download AI Analysis", ai_output.getvalue(), 
                             "ai_analysis.xlsx", 
                             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# [Rest of your existing code remains the same]
